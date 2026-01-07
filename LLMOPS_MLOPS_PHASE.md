# LLMOps & MLOps Infrastructure

This document outlines the current observability solutions and the roadmap for professional deployment.

## Phase Overview: The "Mid-Solution" (Current)

We have transitioned from manual logging to a **Unified System Dashboard**. This provides a 360-degree view of your recommendation engine's health.

### 1. Unified Observability Dashboard
Run the following to generate the latest report:
```powershell
.\venv\Scripts\python.exe scripts/generate_dashboard.py
```
**Features:**
- **LLM Accuracy Tracker**: Real-time evaluation against a "Gold Standard" dataset (87.5%+ accuracy).
- **Genre Recall Metrics**: Measures how well the LLM maps human speech to database categories.
- **ML Model Metadata**: Displays the active Collaborative Filtering (SVD) model, its parameters, and training size.
- **System Trace**: Side-by-side comparison of every test query and the LLM's interpretation.

### 2. Automated Feedback Logging
All user swipes are captured in `data/feedback.jsonl`. This forms the raw material for our next phase.

---

## The "Future Solution" (Professional Implementation)

### 1. Advanced MLOps (W&B / MLflow)
- **Goal**: Track model performance over months, not just days.
- **Implementation**: Integrate the `wandb` library into `src/training.py` to upload loss curves and validation metrics automatically.
- **Benefit**: Visualizes "Concept Drift" (when user tastes change) and triggers automatic retraining.

### 2. Conversational Guardrails (LangSmith)
- **Goal**: Full traceability of every LLM reasoning step.
- **Implementation**: Add the `LANGCHAIN_TRACING_V2=true` environment variable.
- **Benefit**: Allows you to "debug" why a specific user query led to a bad recommendation without re-running the script.

### 3. Automated Feedback Harvester (The "Flywheel")
- **Goal**: The system gets smarter automatically.
- **Implementation**:
    1. A cron job reads `feedback.jsonl`.
    2. Any movie liked by the user but *not* predicted by the LLM (or vice versa) is added to `data/eval_dataset.json`.
    3. The `generate_dashboard.py` runs automatically every night.
- **Benefit**: Continuous improvement cycle without human intervention.
