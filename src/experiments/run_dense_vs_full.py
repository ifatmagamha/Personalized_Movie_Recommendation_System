import subprocess


def run(cmd: str):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    print(" Experiment: Dense CF vs Full CF Dataset ")

    # CF trained on full interactions
    run(
        "python -m src.evaluation "
        "--mode cf "
        "--k 10 "
        "--holdout last1 "
        "--candidate_pool 2000 "
        "--interactions data/interactions.parquet"
    )

    # CF trained on dense interactions
    run(
        "python -m src.evaluation "
        "--mode cf "
        "--k 10 "
        "--holdout last1 "
        "--candidate_pool 2000 "
        "--interactions data/cf_interactions.parquet"
    )

    print("\n[OK] Dense vs full CF experiment completed.")
