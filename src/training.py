from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class TrainConfig:
    interactions_path: str = "data/interactions.parquet"
    movies_path: Optional[str] = "data/movies.parquet"  
    out_dir: str = "models"
    topn: int = 2000
    min_ratings: int = 20  # stability for popularity table
    bayes_m: int = 50      # Bayesian smoothing strength (m)
    seed: int = 42

    # CF params 
    train_cf: bool = False
    cf_model: str = "svd"  
    cf_factors: int = 100
    cf_epochs: int = 20
    cf_lr_all: float = 0.005
    cf_reg_all: float = 0.02


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_interactions(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    required = {"userId", "movieId", "rating"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"interactions missing columns: {missing}")

    # timestamp is optional for training baseline/cf here
    df = df.dropna(subset=["userId", "movieId", "rating"]).copy()

    # enforce types (safe)
    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)
    df["rating"] = df["rating"].astype(float)
    return df


def _load_movies(path: Optional[str]) -> Optional[pd.DataFrame]:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    # Keep only useful cols if present
    keep = [c for c in ["movieId", "title", "genres"] if c in df.columns]
    if "movieId" not in keep:
        return None
    df = df[keep].copy()
    df["movieId"] = df["movieId"].astype(int)
    return df


def build_popularity_table(
    interactions: pd.DataFrame,
    min_ratings: int = 20,
    bayes_m: int = 50,
) -> pd.DataFrame:
    """
    Robust popularity baseline with Bayesian average:
      score = (v/(v+m))*R + (m/(v+m))*C
    where:
      v = n_ratings for the movie
      R = avg_rating for the movie
      C = global mean rating
      m = smoothing strength (bayes_m)
    """
    C = interactions["rating"].mean()

    agg = (
        interactions.groupby("movieId")["rating"]
        .agg(n_ratings="count", avg_rating="mean", std_rating="std")
        .reset_index()
    )
    agg["std_rating"] = agg["std_rating"].fillna(0.0)

    v = agg["n_ratings"].astype(float)
    R = agg["avg_rating"].astype(float)
    m = float(bayes_m)

    agg["bayes_score"] = (v / (v + m)) * R + (m / (v + m)) * C

    # Keep only stable movies
    stable = agg[agg["n_ratings"] >= int(min_ratings)].copy()

    # Sort by bayesian score first, tie-breaker by volume
    stable = stable.sort_values(
        ["bayes_score", "n_ratings"], ascending=[False, False]
    ).reset_index(drop=True)

    return stable


def save_artifacts(
    out_root: Path,
    cfg: TrainConfig,
    popularity: pd.DataFrame,
    movies: Optional[pd.DataFrame],
    cf_info: Optional[Dict] = None,
) -> Path:
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = out_root / f"run_{run_id}"
    _ensure_dir(out_dir)

    # Save config
    cfg_dict = asdict(cfg)
    cfg_dict["run_id"] = run_id
    cfg_dict["utc_time"] = run_id
    (out_dir / "config.json").write_text(json.dumps(cfg_dict, indent=2), encoding="utf-8")

    # Save popularity table
    popularity.to_parquet(out_dir / "top_global.parquet", index=False)

    # Save movies metadata (optional)
    if movies is not None:
        movies.to_parquet(out_dir / "movies.parquet", index=False)

    # Save CF metadata (optional)
    if cf_info:
        (out_dir / "cf_info.json").write_text(json.dumps(cf_info, indent=2), encoding="utf-8")

    # Convenience pointer to "latest"
    latest = out_root / "LATEST"
    latest.write_text(str(out_dir), encoding="utf-8")

    return out_dir


def train_cf_surprise_svd(
    interactions: pd.DataFrame,
    cfg: TrainConfig,
    out_dir: Path,
) -> Dict:
    """
    Optional: Train a collaborative filtering model (Surprise SVD).
    This requires: pip install scikit-surprise
    """
    try:
        from surprise import Dataset, Reader, SVD
        from surprise.model_selection import train_test_split
        import joblib
    except Exception as e:
        raise RuntimeError(
            "Surprise is not installed. Install with: pip install scikit-surprise"
        ) from e

    # Surprise expects (user, item, rating) as strings typically, but ints also fine.
    df = interactions[["userId", "movieId", "rating"]].copy()

    reader = Reader(rating_scale=(df["rating"].min(), df["rating"].max()))
    data = Dataset.load_from_df(df, reader)

    trainset = data.build_full_trainset()

    algo = SVD(
        n_factors=cfg.cf_factors,
        n_epochs=cfg.cf_epochs,
        lr_all=cfg.cf_lr_all,
        reg_all=cfg.cf_reg_all,
        random_state=cfg.seed,
    )
    algo.fit(trainset)

    # Save model
    import joblib
    joblib.dump(algo, out_dir / "cf_svd.joblib")

    # Save mappings to help serving
    # Surprise internally maps raw ids to inner ids; we keep raw sets for quick checks
    cf_info = {
        "model_type": "surprise_svd",
        "n_factors": cfg.cf_factors,
        "n_epochs": cfg.cf_epochs,
        "rating_min": float(df["rating"].min()),
        "rating_max": float(df["rating"].max()),
        "num_users": int(df["userId"].nunique()),
        "num_movies": int(df["movieId"].nunique()),
    }
    return cf_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline (and optional CF) recommender.")
    parser.add_argument("--interactions", default="data/interactions.parquet")
    parser.add_argument("--movies", default="data/movies.parquet")
    parser.add_argument("--out_dir", default="models")
    parser.add_argument("--topn", type=int, default=200)
    parser.add_argument("--min_ratings", type=int, default=20)
    parser.add_argument("--bayes_m", type=int, default=50)

    parser.add_argument("--train_cf", action="store_true")
    parser.add_argument("--cf_factors", type=int, default=100)
    parser.add_argument("--cf_epochs", type=int, default=20)
    parser.add_argument("--cf_lr_all", type=float, default=0.005)
    parser.add_argument("--cf_reg_all", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    cfg = TrainConfig(
        interactions_path=args.interactions,
        movies_path=args.movies,
        out_dir=args.out_dir,
        topn=args.topn,
        min_ratings=args.min_ratings,
        bayes_m=args.bayes_m,
        seed=args.seed,
        train_cf=args.train_cf,
        cf_factors=args.cf_factors,
        cf_epochs=args.cf_epochs,
        cf_lr_all=args.cf_lr_all,
        cf_reg_all=args.cf_reg_all,
    )

    np.random.seed(cfg.seed)

    interactions = _load_interactions(cfg.interactions_path)
    movies = _load_movies(cfg.movies_path)

    pop = build_popularity_table(
        interactions=interactions,
        min_ratings=cfg.min_ratings,
        bayes_m=cfg.bayes_m,
    )

    # keep only Top-N in artifact (fast serving)
    pop_top = pop.head(cfg.topn).copy()

    out_root = Path(cfg.out_dir)
    _ensure_dir(out_root)

    # Save first (baseline)
    out_dir = save_artifacts(out_root, cfg, pop_top, movies, cf_info=None)
    print(f"[OK] Baseline artifacts saved to: {out_dir}")

    # Optional CF
    if cfg.train_cf:
        cf_info = train_cf_surprise_svd(interactions, cfg, out_dir)
        (out_dir / "cf_info.json").write_text(json.dumps(cf_info, indent=2), encoding="utf-8")
        print(f"[OK] CF model saved to: {out_dir / 'cf_svd.joblib'}")


if __name__ == "__main__":
    main()
