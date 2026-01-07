from __future__ import annotations
import argparse
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd().parent
DATA_DIR = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))


def build_cf_interactions(
    input_path: str = "DATA_DIR/interactions.parquet",
    output_path: str = "DATA_DIR/cf_interactions.parquet",
    min_user_ratings: int = 10,
    min_movie_ratings: int = 20,
) -> None:
    df = pd.read_parquet(input_path)[["userId", "movieId", "rating", "timestamp"]].dropna()
    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)

    # Count interactions
    user_counts = df.groupby("userId").size().rename("n_user")
    movie_counts = df.groupby("movieId").size().rename("n_movie")

    df = df.join(user_counts, on="userId").join(movie_counts, on="movieId")
    df_cf = df[(df["n_user"] >= min_user_ratings) & (df["n_movie"] >= min_movie_ratings)].copy()
    df_cf = df_cf.drop(columns=["n_user", "n_movie"])

    df_cf.to_parquet(output_path, index=False)
    print(f"[OK] CF interactions saved: {output_path}")
    print(f"Rows: {len(df_cf):,} | Users: {df_cf['userId'].nunique():,} | Movies: {df_cf['movieId'].nunique():,}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="DATA_DIR/interactions.parquet")
    p.add_argument("--output", default="DATA_DIR/cf_interactions.parquet")
    p.add_argument("--min_user", type=int, default=10)
    p.add_argument("--min_movie", type=int, default=20)
    args = p.parse_args()

    build_cf_interactions(
        input_path=args.input,
        output_path=args.output,
        min_user_ratings=args.min_user,
        min_movie_ratings=args.min_movie,
    )


if __name__ == "__main__":
    main()