import subprocess


def run(cmd: str):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    print(" Experiment: Baseline vs Collaborative Filtering ")

    # Baseline
    run(
        "python -m src.evaluation "
        "--mode baseline "
        "--k 10 "
        "--holdout last1 "
        "--candidate_pool 2000"
    )

    # Collaborative Filtering
    run(
        "python -m src.evaluation "
        "--mode cf "
        "--k 10 "
        "--holdout last1 "
        "--candidate_pool 2000"
    )

    print("\n[OK] Baseline vs CF experiment completed.")
