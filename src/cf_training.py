from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import pandas as pd


@dataclass
class CFConfig:
    interactions_path: str = "data/interactions.parquet"
    models_dir: str = "models"
    seed: int = 42

    # SVD hyperparams 
    n_factors: int = 100
    n_epochs: int = 20
    lr_all: float = 0.005
    reg_all: float = 0.02

    # Speed / memory
    train_on_sample: bool = False
    sample_n: int = 2_000_000  


def load_interactions(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    for c in ["userId", "movieId", "rating"]:
        if c not in df.columns:
            raise ValueError(f"Missing column in interactions: {c}")
    df = df.dropna(subset=["userId", "movieId", "rating"]).copy()
    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)
    df["rating"] = df["rating"].astype(float)
    return df


def get_latest_run_dir(models_dir: str) -> Path:
    p = Path(models_dir)
    latest = p / "LATEST"
    if not latest.exists():
        raise FileNotFoundError("models/LATEST not found. Run baseline training first.")
    run_dir = Path(latest.read_text(encoding="utf-8").strip())
    if not run_dir.exists():
        raise FileNotFoundError(f"LATEST points to missing directory: {run_dir}")
    return run_dir


def train_svd(df: pd.DataFrame, cfg: CFConfig):
    # surprise imports
    from surprise import Dataset, Reader, SVD
    import joblib

    # determine rating scale (MovieLens typically 0.5 to 5.0)
    rmin = float(df["rating"].min())
    rmax = float(df["rating"].max())
    reader = Reader(rating_scale=(rmin, rmax))

    data = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
    trainset = data.build_full_trainset()

    algo = SVD(
        n_factors=cfg.n_factors,
        n_epochs=cfg.n_epochs,
        lr_all=cfg.lr_all,
        reg_all=cfg.reg_all,
        random_state=cfg.seed,
    )
    algo.fit(trainset)
    return algo, {"rating_min": rmin, "rating_max": rmax}


def main():
    cfg = CFConfig()

    df = load_interactions(cfg.interactions_path)

    # sampling for speed if dataset is huge
    if cfg.train_on_sample and len(df) > cfg.sample_n:
        df = df.sample(cfg.sample_n, random_state=cfg.seed).copy()

    algo, scale_info = train_svd(df, cfg)

    run_dir = get_latest_run_dir(cfg.models_dir)

    # save model inside the current latest run (same run folder as baseline)
    import joblib
    model_path = run_dir / "cf_svd.joblib"
    joblib.dump(algo, model_path)

    cf_info = {
        **asdict(cfg),
        **scale_info,
        "trained_rows": int(len(df)),
        "num_users": int(df["userId"].nunique()),
        "num_movies": int(df["movieId"].nunique()),
        "trained_at_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model_type": "surprise_svd",
    }
    (run_dir / "cf_info.json").write_text(json.dumps(cf_info, indent=2), encoding="utf-8")

    print(f"[OK] CF model saved: {model_path}")
    print(f"[OK] CF info saved:  {run_dir / 'cf_info.json'}")


if __name__ == "__main__":
    main()
