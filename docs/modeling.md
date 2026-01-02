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

These datasets represent the **source of truth** for modeling.

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
