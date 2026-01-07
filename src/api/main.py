from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.api.schemas import (
    RecommendRequest, RecommendResponse, MovieRecommendation,
    FeedbackRequest, FeedbackResponse,
    GenresResponse
)
from src.llm.intent_parser import parse_mood_to_filters
from src.llm.reasoning import generate_reason
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

@app.get("/")
def root():
    return RedirectResponse(url=f"{settings.ROOT_PATH}/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"api_version": app.version, "root_path": settings.ROOT_PATH}


@app.post("/admin/reload")
def reload_model():
    """Force reload of the recommender model"""
    get_recommender.cache_clear()
    # Warm up
    r = get_recommender()
    return {
        "status": "reloaded", 
        "run_dir": str(r.run_dir),
        "cf_enabled": r.cf_enabled
    }


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


from datetime import datetime
from src.llm.intent_parser import parse_mood_to_filters
from src.llm.reasoning import generate_reason

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    r = get_recommender()
    constraints = req.constraints or {}

    # 1. Model Selection Heuristic (Orchestration Layer)
    user_id = req.user_id
    mode = (req.mode or "auto").lower()
    
    can_use_cf = (r.cf_enabled and user_id is not None)

    if mode == "auto":
        seen_count = 0
        if can_use_cf:
            try:
                r._load_user_seen()
                seen_count = len(r._user_seen.get(int(user_id), set()))
            except: pass
        
        # Add real-time swiped movies to the count if provided in constraints
        swiped_ids = constraints.get("exclude_movieIds", [])
        total_history_signal = seen_count + len(swiped_ids)

        # Decision: Use CF only if user has 5+ interactions total (Historical + Current Session)
        if can_use_cf and total_history_signal >= 5:
            mode = "cf"
        else:
            mode = "baseline"
        print(f"[INFO] Orchestrator selected mode: {mode} (history={seen_count}, swiped={len(swiped_ids)})")

    # 2. LLM Intent Parsing
    intent_obj = None
    
    if req.query and len(req.query.strip()) > 2:
        print(f"[INFO] Triggering LLM Intent Parser for query: '{req.query}'")
        intent_obj = parse_mood_to_filters(req.query)
        print(f"[INFO] LLM Intent: {intent_obj}")

    # Map LLM Intent Object (New Schema) to Recommendation Constraints
    llm_expl = None
    if intent_obj:
        llm_expl = intent_obj.get("explanation")
        llm_c = intent_obj.get("constraints", {})
        
        # Merge genres (LLM + existing manual)
        llm_genres = set(llm_c.get("genres") or [])
        if llm_genres:
            existing_in = set(constraints.get("genres_in") or [])
            constraints["genres_in"] = list(existing_in | llm_genres)
        
        # Map year_range [min, max]
        yr = llm_c.get("year_range")
        if yr and isinstance(yr, list) and len(yr) == 2:
            if "min_year" not in constraints: constraints["min_year"] = yr[0]
            if "max_year" not in constraints: constraints["max_year"] = yr[1]

    # 3. Recommendation Generation
    print(f"[INFO] Generating recommendations: mode={mode}, k={req.k}, constraints={list(constraints.keys())}")
    df = r.recommend(
        user_id=user_id,
        k=int(req.k),
        mode=mode,
        candidate_pool=int(req.candidate_pool),
        constraints=constraints
    )

    # 4. Enforce Baseline Fallback if results are empty
    # If the first attempt (with all constraints) is empty, it's often because of a too-strict year or genre filter.
    if df.empty:
        print("[WARN] No results found with full constraints. Relaxing restrictions...")
        
        # Try 1: Keep genres/mood but drop year/rating constraints
        relaxed_constraints = {
            "genres_in": constraints.get("genres_in"),
            "exclude_movieIds": constraints.get("exclude_movieIds")
        }
        df = r.recommend_baseline(user_id=user_id, k=int(req.k), constraints=relaxed_constraints)
        
        # If still empty, Final safety net (global favorites)
        if df.empty:
            print("[WARN] Final safety net: Serving global top picked directly.")
            df = r.recommend_baseline(user_id=user_id, k=int(req.k))

    # 5. Enrich with Explanations & Metadata
    recs = []
    
    # Fetch user liked titles for the reasoning engine
    user_liked_titles = []
    if user_id:
        try:
            ix = pd.read_parquet("data/interactions.parquet")
            u_likes = ix[(ix["userId"] == user_id) & (ix["rating"] >= 4.0)].sort_values("timestamp", ascending=False).head(5)
            if not u_likes.empty and r.movies_df is not None:
                liked_ids = u_likes["movieId"].tolist()
                user_liked_titles = r.movies_df[r.movies_df["movieId"].isin(liked_ids)]["title"].tolist()
        except: pass

    for i, (_, row) in enumerate(df.iterrows()):
        # Reasoning Priority:
        # 1. LLM "explanation" from intent (for top 1)
        # 2. Reasoning Engine (for top 3)
        # 3. Fallback logic
        reason = "Recommended for you."
        if i == 0 and llm_expl:
            reason = llm_expl
        elif user_liked_titles and i < 3:
            reason = generate_reason(user_liked_titles, row["title"], row.get("genres", ""))
        elif "genres" in row:
            top_g = row["genres"].split("|")[0]
            reason = f"A top choice for {top_g} lovers."

        recs.append(MovieRecommendation(
            movieId=int(row["movieId"]),
            title=row["title"],
            genres=row.get("genres"),
            score=float(row.get("cf_score") if mode=="cf" else row.get("bayes_score", 0.0)),
            reason=reason,
            year=int(row["year"]) if pd.notnull(row.get("year")) else None,
            rating=float(row["rating"]) if "rating" in row else None,
            description=row.get("description"),
            poster=row.get("poster") or f"https://via.placeholder.com/300x450?text={row['title']}",
            backdrop=row.get("backdrop"),
            duration=int(row["duration"]) if pd.notnull(row.get("duration")) else None
        ))

    intent_debug = {
        "mode": mode,
        "llm_parsed": intent_obj,
        "final_constraints": {k: v for k, v in constraints.items() if v}
    }

    return RecommendResponse(
        intent=intent_debug,
        recommendations=recs
    )


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

    return FeedbackResponse(status="success", received=payload)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
