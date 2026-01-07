
# MLOps Manual: The Feedback Loop

This document describes how to execute the **Data-to-Model Feedback Loop** (Phase 3).

## Overview
The system captures user interactions (likes/dislikes) in `data/feedback.jsonl`.
The MLOps pipeline merges this feedback into the historical dataset (`interactions.parquet`) and retrains the SVD model.

## 0. Prerequisites
Ensure the backend is running:
```bash
python -m src.api.main
```
(Or use `npm run dev` for the UI to generate some feedback first).

## 1. ETL Step (Merge Feedback)
Run the merge script to process pending feedback.
```bash
.\venv\Scripts\python.exe src/etl/merge_feedback.py
```
*   **Input**: `data/feedback.jsonl`
*   **Output**: Updates `data/interactions.parquet`
*   **Archive**: Moves jsonl to `data/archive/`

## 2. Retraining Step (Train Model)
Train a new Collaborative Filtering model using the updated interactions.
```bash
.\venv\Scripts\python.exe src/training.py --train_cf
```
*   **Output**: New folder in `models/run_YYYYMMDD_HHMMSS/`
*   **Pointer**: Updates `models/LATEST`

## 3. Deployment Step (Hot Reload)
Tell the running API to switch to the new model without downtime.
```bash
curl -X POST http://localhost:8000/admin/reload
```
*   **Response**: `{"status": "reloaded", "run_dir": "models/run_...", "cf_enabled": true}`

## validation
To verify the new model is active:
1.  Check the response of `/admin/reload`.
2.  Or check `data/interactions.parquet` row count.
