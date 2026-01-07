# Modeling – Training Phase Documentation

## Overview
This document describes the **training phase** of the movie recommendation system implemented so far.

The objective of this phase is to move from exploratory data analysis (EDA) to **production-oriented model artifacts** that can be reliably used for inference, evaluation, and deployment.

At this stage, we focused on:
- Building a **robust baseline recommender**
- Structuring model artifacts in a reproducible and deployable way
- Preparing the ground for collaborative filtering and further iterations

---

## Context and Constraints

- **Data source**: BigQuery (`master-ai-cloud.MoviePlatform`)
- **Access level**: Read-only
- **Strategy**:
  - Perform all heavy preprocessing once
  - Export filtered datasets locally as Parquet
  - Run training and modeling entirely offline (no BigQuery dependency)

This approach:
- Reduces BigQuery costs
- Improves iteration speed
- Matches production-grade ML workflows

---

## Inputs to the Training Phase

The training pipeline consumes **derived datasets** produced during the preprocessing and EDA phase:

- `data/interactions.parquet`
  - Columns: `userId`, `movieId`, `rating`, `timestamp`
  - Filtered to remove extreme cold-start users and unstable items

These datasets represent the **ground truth** for modeling.

---

## Training Script: `src/training.py`

### Design Philosophy

The training logic is implemented as a **standalone script**, not a notebook, in order to:
- Ensure reproducibility
- Enable automated execution (CI/CD, Docker, Cloud Run, Vertex AI)
- Clearly separate experimentation from production logic

The script is intentionally **modular**, using:
- A configuration object (`TrainConfig`)
- Small, focused helper functions
- Explicit artifact saving

---

### Configuration Management

A configuration dataclass is used:

```python
@dataclass
class TrainConfig:
    interactions_path: str
    out_dir: str
    topn: int
    min_ratings: int
    bayes_m: int
    seed: int

# Recommendation Pipeline (Training → Prediction → Evaluation)

## 1. Goal
Build a robust and reproducible recommendation pipeline.
We implement:
- An offline training step that produces versioned model artifacts
- An online prediction layer that loads the latest artifacts
- An offline evaluation protocol with time-based splitting and ranking metrics

---

## 2. Training (`src/training.py`)
### Responsibility
- Read derived datasets (`data/interactions.parquet`)
- Build models (baseline now, CF later)
- Save versioned artifacts under `models/run_<timestamp>/`
- Update `models/LATEST`

### Baseline Model (Popularity + Bayesian Smoothing)
For each movie:
- `n_ratings`, `avg_rating`
We compute a robust score:

score = (v/(v+m))*R + (m/(v+m))*C

Where:
- v = movie rating count
- R = movie mean rating
- C = global mean rating
- m = smoothing strength

We store Top-N movies in `top_global.parquet`.

---

## 3. Prediction (`src/prediction.py`)
### Responsibility
- Load artifacts from the latest run pointed by `models/LATEST`
- Return Top-K recommendations
- Filter out items already seen by the user (from interaction history)

### Modes
- baseline: returns Top-K from `top_global`
- cf: reranks candidates using CF model if available
- auto: uses CF if available, otherwise fallback baseline

---

## 4. Evaluation (`src/evaluation.py`)
### Responsibility
Measure recommendation quality in an offline simulation.

### Time-Based Split
To avoid using future information:
- For each user, interactions are sorted by timestamp
- Train = older interactions
- Test = most recent interactions (holdout)

Modes:
- last1: last interaction in test
- lastpct: last X% in test

### Leakage Fix (Critical)
During evaluation, the “seen items” filter must be built from TRAIN only.
Otherwise, the test item gets removed from candidates and metrics become artificially 0.

Implementation:
- we instantiate the recommender with `interactions_df=train_df`

### Metrics
- Recall@K: fraction of relevant items retrieved in top-K
- NDCG@K: ranking quality with higher weight for early hits

Outputs:
- terminal summary (mean metrics)
- `models/eval_report.csv` per-user metrics

---

## 5. Execution
Prediction test:
```bash
python -m src.prediction
