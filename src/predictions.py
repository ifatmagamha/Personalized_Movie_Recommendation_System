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
        interactions_df: Optional[pd.DataFrame] = None,  # <-- KEY FIX
    ) -> None:
        self.paths = ModelPaths(Path(models_dir))
        self.run_dir = self.paths.latest_run_dir()

        self.interactions_path = Path(interactions_path)
        self._interactions_df = interactions_df  # if provided, use it to build "seen"
        self._user_seen: Optional[Dict[int, set]] = None

        # load artifacts
        top_path = self.run_dir / "top_global.parquet"
        if not top_path.exists():
            raise FileNotFoundError(f"Missing artifact: {top_path}")
        self.top_global = pd.read_parquet(top_path)

        movies_path = self.run_dir / "movies.parquet"
        self.movies = pd.read_parquet(movies_path) if movies_path.exists() else None

        # CF
        self.cf_enabled = False
        self.cf_model = None
        cf_path = self.run_dir / "cf_svd.joblib"
        if cf_path.exists():
            try:
                import joblib
                self.cf_model = joblib.load(cf_path)
                self.cf_enabled = True
            except Exception:
                self.cf_model = None
                self.cf_enabled = False

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
            return recs
        return recs.merge(self.movies, on="movieId", how="left")

    def recommend_baseline(self, user_id: Optional[int], k: int = 10) -> pd.DataFrame:
        df = self.top_global.copy()

        if user_id is not None:
            self._load_user_seen()
            seen = self._user_seen.get(int(user_id), set()) if self._user_seen else set()
            if seen:
                df = df[~df["movieId"].isin(seen)]

        df = df.head(int(k)).copy()
        df = self._enrich(df)

        cols = [c for c in ["movieId", "bayes_score", "n_ratings", "avg_rating", "title", "genres"] if c in df.columns]
        return df[cols]

    def recommend_cf(self, user_id: int, k: int = 10, candidate_pool: int = 500) -> pd.DataFrame:
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

        cols = [c for c in ["movieId", "cf_score", "bayes_score", "n_ratings", "avg_rating", "title", "genres"] if c in cand.columns]
        return cand[cols]

    def recommend(self, user_id: Optional[int], k: int = 10, mode: str = "auto") -> pd.DataFrame:
        mode = (mode or "auto").lower()
        if mode == "baseline":
            return self.recommend_baseline(user_id=user_id, k=k)
        if mode == "cf":
            if user_id is None:
                return self.recommend_baseline(user_id=None, k=k)
            return self.recommend_cf(user_id=int(user_id), k=k)

        # auto
        if user_id is not None and self.cf_enabled:
            return self.recommend_cf(user_id=int(user_id), k=k)
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
