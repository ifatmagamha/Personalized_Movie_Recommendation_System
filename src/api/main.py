from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.api.schemas import (
    RecommendRequest, RecommendResponse,
    FeedbackRequest, FeedbackResponse,
    GenresResponse
)
from src.api.deps import get_recommender
from src.api.settings import settings
from src.api.filters import apply_filters

app = FastAPI(
    title="OFF Hours — Hybrid Movie Recommendation API",
    description="Baseline (popular) + CF (personalized). LLM layer optional later.",
    version="0.1.0",
    root_path=settings.ROOT_PATH,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"api_version": app.version, "root_path": settings.ROOT_PATH}


@app.get("/genres", response_model=GenresResponse)
def genres():
    r = get_recommender()
    if r.movies is None or "genres" not in r.movies.columns:
        return {"genres": []}

    s = r.movies["genres"].dropna().astype(str)
    all_genres = set()
    for g in s:
        for part in g.split("|"):
            part = part.strip()
            if part:
                all_genres.add(part)

    return {"genres": sorted(all_genres)}


def _default_reason(mode: str) -> str:
    if mode == "baseline":
        return "Popular picks based on global ratings and popularity."
    if mode == "cf":
        return "Personalized picks based on similar users' ratings."
    return "Personalized if possible, otherwise popular picks."


def _safe(row, key, cast=None):
    v = row.get(key, None)
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if pd.isna(v):
        return None
    if cast:
        try:
            return cast(v)
        except Exception:
            return None
    return v


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    r = get_recommender()

    intent = {"raw_query": req.query, "mood": None, "constraints": req.constraints or {}}
    user_id = req.user_id if req.user_id is not None else -1
    mode = (req.mode or "auto").lower()

    base_df = r.recommend(
        user_id=int(user_id),
        k=int(req.k),
        mode=mode,
        candidate_pool=int(req.candidate_pool),
    )

    # --- apply constraints ---
    c = req.constraints or {}
    df = apply_filters(
        base_df,
        include_genres=c.get("genres_in", []),
        exclude_genres=c.get("genres_out", []),
        min_n_ratings=c.get("min_n_ratings", None),
        min_avg_rating=c.get("min_avg_rating", None),
        exclude_movieIds=c.get("exclude_movieIds", None),
    )

    if df.empty:
        df = base_df

    df = df.head(int(req.k)).copy()
        
    recs = []
    for _, row in df.iterrows():
        score = float(row.get("cf_score", row.get("bayes_score", 0.0)))

        recs.append({
            "movieId": int(row["movieId"]),
            "title": row.get("title", ""),
            "genres": row.get("genres"),
            "score": score,
            "reason": _default_reason(mode),

            # enrich fields (optional)
            "year": (None if pd.isna(row.get("year")) else int(row.get("year")) ) if "year" in row else None,
            "rating": (None if pd.isna(row.get("rating")) else float(row.get("rating")) ) if "rating" in row else None,
            "description": row.get("description"),
            "duration": (None if pd.isna(row.get("duration")) else int(row.get("duration")) ) if "duration" in row else None,
            "poster": row.get("poster"),
            "backdrop": row.get("backdrop"),
        })


    return {"intent": intent, "recommendations": recs}


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest):
    # append-only JSONL (safe & simple)
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = out_dir / "feedback.jsonl"

    payload = req.model_dump()
    payload["_ts"] = datetime.utcnow().isoformat()

    with fp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return {"status": "ok", "received": req.model_dump()}
