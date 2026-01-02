# Recommendation Pipeline (Training → Prediction → Evaluation)

## 1. Goal
Build a robust and reproducible recommendation pipeline under BigQuery read-only constraints.
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
