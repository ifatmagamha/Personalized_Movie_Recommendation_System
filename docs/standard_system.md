# Standard System Description

## 1. Recommendation Logic Audit

### Model Architecture
The system employs a **Hybrid Recommendation Engine** compatible with `scikit-surprise`.
*   **User-Based Collaborative Filtering (CF)**: 
    *   Uses **SVD (Singular Value Decomposition)** for matrix factorization.
    *   Input: `(userId, movieId, rating)` tuples.
    *   Output: Predicted rating for a given `(user, movie)` pair.
    *   Library: `scikit-surprise`.
    *   Training: Minimizes RMSE on explicit ratings.
*   **Baseline (Popularity)**:
    *   Used when user history is insufficient (Cold Start) or CF model is disabled.
    *   Logic: **Bayesian Average** smoothing (`(v/(v+m))*R + (m/(v+m))*C`).
    *   Ensures that movies with few 5-star ratings don't outrank stable blockbusters.

### Data Flow
1.  **Selection**: The recommender selects a pool of candidates (e.g., top 2000 popular movies OR predicted top-k from SVD).
2.  **Enrichment**: Movie IDs are enriched with metadata (posters, plots) from `movies_enriched.parquet`.
3.  **Filtering (Post-Process)**:
    *   Filters (Genres, Min Rating, Popularity) are applied **after** the candidate generation.
    *   **Implication**: If a user selects "Documentary" (rare genre) and the initial pool of 2000 recommendations only contains 2 documentaries, the UI will only show 2 results.
    *   Files: `src/api/filters.py` handles the dataframe masking.

## 2. Feedback Data (`feedback.jsonl`)

### Purpose
The `data/feedback.jsonl` file serves as a **Feature Store for Online Learning / Offline Retraining**.
It captures user intent signals that are not yet part of the stable `interactions.parquet`.

### Schema
Events recorded:
*   `like` / `dislike` (Explicit preference)
*   `skip` (Implicit disinterest)
*   `helpful` / `not_helpful` (Quality feedback)

### Consumption Strategy
*   **Current State**: Write-only (Log collection).
*   **Target State**:
    *   **Offline**: Periodically merge `feedback.jsonl` into `interactions.parquet` to retrain SVD (e.g., nightly).
    *   **Online**: Use immediate session context (list of `swiped_ids`) to filter/re-rank in real-time (as implemented in the "Refine" fix).

## 3. MLOps Strategy (Incremental)

We adhere to a file-based MLOps approach suitable for this scale.

### Versioning
*   **Data**: `data/*.parquet` files are the source of truth.
*   **Models**: Stored in `models/run_YYYYMMDD_HHMMSS/`.
*   **Pointer**: `models/LATEST` text file contains the path to the currently active production model.

### Training Pipeline
1.  **Trigger**: Scheduled cron job or manual invoke.
2.  **Script**: `python src/training.py --train_cf`.
3.  **Atomic Swap**: The API reads `models/LATEST`. Updating this file atomically switches traffic to the new model without downtime (thanks to `lru_cache` expiration or restart).

### Monitoring
*   **Drift**: Compare `avg_rating` distribution in `feedback.jsonl` vs `interactions.parquet`.

## 4. LLM Integration Plan (LangChain)

### Objective
Enhance the "Reasons" and "Search" capabilities without replacing the core CF engine.

### Integration Points
1.  **Natural Language Search**:
    *   **Input**: "I want a sad movie about space."
    *   **LLM Role**: Translate to structured constraints -> `{ "genre": "Sci-Fi", "keywords": ["space", "astronaut"], "sentiment": "sad" }`.
2.  **Explanation**:
    *   **Input**: Movie Metadata + User History.
    *   **LLM Role**: Generate "Why you might like this" blurb.
    *   **Implementation**: `LangChain` chain calling OpenAI/Gemini, cached by `movieId`.

