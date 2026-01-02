from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

import numpy as np
import pandas as pd

from src.predictions import load_recommender


@dataclass
class EvalConfig:
    interactions_path: str = "data/interactions.parquet"
    k: int = 10
    mode: str = "baseline"     # baseline | cf | auto
    holdout: str = "last1"     # last1 | lastpct
    holdout_pct: float = 0.2
    max_users: int | None = 2000
    seed: int = 42


def split_by_user_time(
    interactions: pd.DataFrame,
    holdout: str = "last1",
    holdout_pct: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Time-based split PER USER to avoid looking into the future.
    - last1: last interaction per user goes to test
    - lastpct: last X% interactions per user go to test
    """
    df = interactions.dropna(subset=["userId", "movieId", "timestamp"]).copy()
    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)
    df = df.sort_values(["userId", "timestamp"])

    train_parts, test_parts = [], []
    for uid, grp in df.groupby("userId", sort=False):
        n = len(grp)
        if n < 2:
            continue

        if holdout == "last1":
            cut = n - 1
        elif holdout == "lastpct":
            test_size = max(1, int(np.ceil(n * holdout_pct)))
            cut = n - test_size
        else:
            raise ValueError("holdout must be 'last1' or 'lastpct'")

        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])

    train_df = pd.concat(train_parts, ignore_index=True) if train_parts else df.iloc[0:0]
    test_df = pd.concat(test_parts, ignore_index=True) if test_parts else df.iloc[0:0]
    return train_df, test_df


def recall_at_k(recommended: List[int], relevant: set, k: int) -> float:
    if not relevant:
        return np.nan
    hit = len(set(recommended[:k]) & relevant)
    return hit / float(len(relevant))


def ndcg_at_k(recommended: List[int], relevant: set, k: int) -> float:
    rec_k = recommended[:k]
    dcg = 0.0
    for i, item in enumerate(rec_k, start=1):
        if item in relevant:
            dcg += 1.0 / np.log2(i + 1)

    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / np.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else np.nan


def evaluate(
    recommender,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    k: int = 10,
    mode: str = "baseline",
    max_users: int | None = 2000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Evaluate recommender on a time-based holdout:
    - Relevant items for each user = items in TEST
    - Recommendations = top-k produced from TRAIN history
    """
    user_to_relevant: Dict[int, set] = (
        test_df.groupby("userId")["movieId"]
        .apply(lambda s: set(map(int, s.values)))
        .to_dict()
        if len(test_df) else {}
    )

    users = np.array(list(user_to_relevant.keys()), dtype=int)
    rng = np.random.default_rng(seed)
    if max_users is not None and len(users) > max_users:
        users = rng.choice(users, size=max_users, replace=False)

    rows = []
    for uid in users:
        relevant = user_to_relevant.get(int(uid), set())
        recs_df = recommender.recommend(user_id=int(uid), k=k, mode=mode)
        recommended = recs_df["movieId"].astype(int).tolist() if "movieId" in recs_df.columns else []

        rows.append({
            "userId": int(uid),
            "n_relevant": len(relevant),
            f"recall@{k}": recall_at_k(recommended, relevant, k),
            f"ndcg@{k}": ndcg_at_k(recommended, relevant, k),
        })

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactions", default="data/interactions.parquet")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--mode", default="baseline")          # baseline|cf|auto
    parser.add_argument("--holdout", default="last1")          # last1|lastpct
    parser.add_argument("--holdout_pct", type=float, default=0.2)
    parser.add_argument("--max_users", type=int, default=2000)
    args = parser.parse_args()

    cfg = EvalConfig(
        interactions_path=args.interactions,
        k=args.k,
        mode=args.mode,
        holdout=args.holdout,
        holdout_pct=args.holdout_pct,
        max_users=args.max_users,
    )

    interactions = pd.read_parquet(cfg.interactions_path)
    train_df, test_df = split_by_user_time(interactions, holdout=cfg.holdout, holdout_pct=cfg.holdout_pct)

    # build recommender with TRAIN interactions only (avoid leakage)
    rec = load_recommender(interactions_df=train_df)

    per_user = evaluate(
        recommender=rec,
        train_df=train_df,
        test_df=test_df,
        k=cfg.k,
        mode=cfg.mode,
        max_users=cfg.max_users,
        seed=cfg.seed,
    )

    summary = per_user[[f"recall@{cfg.k}", f"ndcg@{cfg.k}"]].mean(numeric_only=True)
    print("\n=== Summary ===")
    print(summary)
    

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    # to avoid overwriting the eval files 
    out_path = Path("models") / f"eval_{cfg.mode}_{ts}.csv"

    # out_path = Path("models") / "eval_report.csv"
    per_user.to_csv(out_path, index=False)
    print(f"\nPer-user report saved to: {out_path}")


if __name__ == "__main__":
    main()
