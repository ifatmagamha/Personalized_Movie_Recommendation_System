from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass
class ModelPaths:
    models_dir: Path = Path("models")

    def latest_run_dir(self) -> Path:
        latest_file = self.models_dir / "LATEST"
        if not latest_file.exists():
            raise FileNotFoundError(f"Missing {latest_file}. Run training first.")
        run_dir = Path(latest_file.read_text(encoding="utf-8").strip())
        if not run_dir.exists():
            raise FileNotFoundError(f"LATEST points to missing dir: {run_dir}")
        return run_dir


class Recommender:
    """
    Serving-time recommender.
    - Baseline: Bayesian-smoothed popularity ranking (top_global.parquet)
    - CF: Surprise SVD model (cf_svd.joblib)
    """

    def __init__(
        self,
        models_dir: str = "models",
        interactions_path: str = "data/interactions.parquet",
        interactions_df: Optional[pd.DataFrame] = None, 
    ) -> None:
        self.paths = ModelPaths(Path(models_dir))

        # 1. Always load data/movies_enriched.parquet first (Source of Truth for UI)
        movies_enriched_path = Path("data/movies_enriched.parquet")
        self.movies = None
        if movies_enriched_path.exists():
            print(f"[INFO] Loading enriched movies from {movies_enriched_path}")
            self.movies = pd.read_parquet(movies_enriched_path)
        
        # 2. Try to load attributes from training run (Models)
        self.top_global = None
        self.cf_model = None
        self.cf_enabled = False
        
        try:
            self.run_dir = self.paths.latest_run_dir()
            
            # Load baseline (top_global)
            top_path = self.run_dir / "top_global.parquet"
            if top_path.exists():
                self.top_global = pd.read_parquet(top_path)
            
            # Load CF
            cf_path = self.run_dir / "cf_svd.joblib"
            if cf_path.exists():
                try:
                    import joblib
                    self.cf_model = joblib.load(cf_path)
                    self.cf_enabled = True
                except Exception:
                    print("[WARN] Failed to load CF model, skipping.")

            # Fallback for movies if not enriched
            if self.movies is None:
                movies_path = self.run_dir / "movies.parquet"
                if movies_path.exists():
                    self.movies = pd.read_parquet(movies_path)

        except Exception as e:
            print(f"[WARN] Model artifacts not found or invalid ({e}). Running in DATA-ONLY mode.")

        self.interactions_path = Path(interactions_path)
        self._interactions_df = interactions_df
        self._user_seen: Optional[Dict[int, set]] = None

        # 3. Critical Fallback: If top_global is missing, create it from movies
        if self.top_global is None:
            if self.movies is not None:
                # Create a dummy popularity table from available movies
                print("[INFO] Creating fallback baseline from movies_enriched")
                self.top_global = self.movies.copy()
                # Ensure compatibility columns
                for col in ["bayes_score", "n_ratings", "avg_rating"]:
                    if col not in self.top_global.columns:
                        self.top_global[col] = 0.0
            else:
                # Last resort empty
                self.top_global = pd.DataFrame(columns=["movieId", "bayes_score"])


    def _load_user_seen(self) -> None:
        """
        Build user -> seen movieIds.
        IMPORTANT:
        - In production: read from full interactions parquet
        - In evaluation: interactions_df should be TRAIN ONLY (to avoid leakage)
        """
        if self._user_seen is not None:
            return

        if self._interactions_df is not None:
            df = self._interactions_df[["userId", "movieId"]].copy()
        else:
            if not self.interactions_path.exists():
                raise FileNotFoundError(f"Missing interactions parquet: {self.interactions_path}")
            df = pd.read_parquet(self.interactions_path, columns=["userId", "movieId"])

        df = df.dropna(subset=["userId", "movieId"]).copy()
        df["userId"] = df["userId"].astype(int)
        df["movieId"] = df["movieId"].astype(int)

        user_seen: Dict[int, set] = {}
        for uid, grp in df.groupby("userId")["movieId"]:
            user_seen[int(uid)] = set(map(int, grp.values))
        self._user_seen = user_seen

    def _enrich(self, recs: pd.DataFrame) -> pd.DataFrame:
        if self.movies is None:
            print("[WARN] _enrich: movies_enriched.parquet not loaded")
            return recs
        
        if recs.empty:
            return recs
        
        # Verify movieId column exists
        if "movieId" not in recs.columns:
            print("[ERROR] _enrich: recs missing 'movieId' column")
            return recs
        
        if "movieId" not in self.movies.columns:
            print("[ERROR] _enrich: movies missing 'movieId' column")
            return recs
        
        # Identify columns to add (avoid duplicates/_x/_y suffixes)
        # We always merge on 'movieId'
        existing = set(recs.columns)
        cols_to_add = [c for c in self.movies.columns if c not in existing and c != "movieId"]
        
        if not cols_to_add:
            return recs
        
        # Perform merge and log results
        merged = recs.merge(
            self.movies[["movieId"] + cols_to_add], 
            on="movieId", 
            how="left"
        )
        
        # Validate merge success
        if len(merged) != len(recs):
            print(f"[WARN] _enrich: merge changed row count {len(recs)} -> {len(merged)}")
        
        # Check how many movies were successfully enriched
        enriched_count = merged["title"].notna().sum() if "title" in merged.columns else 0
        poster_count = merged["poster"].notna().sum() if "poster" in merged.columns else 0
        if enriched_count < len(merged):
            print(f"[WARN] _enrich: only {enriched_count}/{len(merged)} movies have title, {poster_count}/{len(merged)} have poster")
        
        return merged

    def recommend_baseline(self, user_id: Optional[int], k: int = 10) -> pd.DataFrame:
        df = self.top_global.copy()

        if user_id is not None:
            self._load_user_seen()
            seen = self._user_seen.get(int(user_id), set()) if self._user_seen else set()
            if seen:
                df = df[~df["movieId"].isin(seen)]

        df = df.head(int(k)).copy()
        df = self._enrich(df)

        # Keep all columns after enrichment (including poster, description, etc.)
        # Only filter out if they don't exist
        cols = [c for c in [
            "movieId", "bayes_score", "n_ratings", "avg_rating", "title", "genres",
            "poster", "backdrop", "description", "year", "rating", "duration"
        ] if c in df.columns]
        return df[cols] if cols else df

    def recommend_cf(self, user_id: int, k: int = 10, candidate_pool: int = 2000)-> pd.DataFrame:
        
        if not self.cf_enabled or self.cf_model is None:
            return self.recommend_baseline(user_id=user_id, k=k)

        self._load_user_seen()
        seen = self._user_seen.get(int(user_id), set()) if self._user_seen else set()

        cand = self.top_global.head(int(candidate_pool)).copy()
        if seen:
            cand = cand[~cand["movieId"].isin(seen)]

        uid = int(user_id)
        scores = []
        for mid in cand["movieId"].astype(int).tolist():
            try:
                est = float(self.cf_model.predict(uid, int(mid)).est)
            except Exception:
                est = np.nan
            scores.append(est)

        cand = cand.assign(cf_score=scores).dropna(subset=["cf_score"])
        cand = cand.sort_values("cf_score", ascending=False).head(int(k)).copy()
        cand = self._enrich(cand)

        # Keep all columns after enrichment (including poster, description, etc.)
        cols = [c for c in [
            "movieId", "cf_score", "bayes_score", "n_ratings", "avg_rating", "title", "genres",
            "poster", "backdrop", "description", "year", "rating", "duration"
        ] if c in cand.columns]
        return cand[cols] if cols else cand


    def recommend(self, user_id: Optional[int], k: int = 10, mode: str = "auto", candidate_pool: int = 2000) -> pd.DataFrame:
        mode = (mode or "auto").lower()
        if mode == "baseline":
            return self.recommend_baseline(user_id=user_id, k=k)
        if mode == "cf":
            # CF requires a valid user_id, use -1 as fallback if None
            uid = user_id if user_id is not None else -1
            return self.recommend_cf(user_id=uid, k=k, candidate_pool=candidate_pool)

        # auto mode: use CF if available and user_id provided, else baseline
        if self.cf_enabled and self.cf_model is not None and user_id is not None:
            return self.recommend_cf(user_id=user_id, k=k, candidate_pool=candidate_pool)
        return self.recommend_baseline(user_id=user_id, k=k)

def load_recommender(
    models_dir: str = "models",
    interactions_path: str = "data/interactions.parquet",
    interactions_df: Optional[pd.DataFrame] = None,
) -> Recommender:
    return Recommender(models_dir=models_dir, interactions_path=interactions_path, interactions_df=interactions_df)


if __name__ == "__main__":
    rec = load_recommender()
    print(rec.recommend(user_id=1, k=10, mode="auto").head(10))
