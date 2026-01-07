import subprocess


def run(cmd: str):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    print(" Experiment: Candidate Pool Size Impact (CF) ")

    pools = [500, 2000]

    for pool in pools:
        print(f"\n--- Candidate pool = {pool} ---")
        run(
            f"python -m src.evaluation "
            f"--mode cf "
            f"--k 10 "
            f"--holdout last1 "
            f"--candidate_pool {pool}"
        )

    print("\n[OK] Candidate pool experiment completed.")
