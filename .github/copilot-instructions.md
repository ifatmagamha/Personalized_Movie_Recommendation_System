# Copilot / Agent instructions — Personalized Movie Recommendation System

Short, actionable pointers for AI coding agents working in this repo.

## Big picture (what to know first)
- Backend: FastAPI app in `src/api` providing endpoints: `/health`, `/version`, `/genres`, `/recommend`, `/feedback` (see `src/api/main.py`).
- Frontend: Vite + React app in `ui/` (dev: `npm run dev`, build: `npm run build`). UI reads `VITE_API_BASE` (defaults to `http://localhost:8000` in `ui/src/lib/api.ts`).
- Models & artifacts: training outputs go into `models/run_YYYYMMDD_HHMMSS/` and a `models/LATEST` file points to the latest run. Key artifacts: `top_global.parquet`, `movies.parquet`, `cf_svd.joblib`, `cf_info.json`.
- Data: parquet files live in `data/` (e.g., `interactions.parquet`, `movies.parquet`, `movies_enriched.parquet`). Preprocessing that queries BigQuery lives in `src/preprocessing.py` (CTE-only SQL style).
- Core inference: `src/predictions.py::Recommender` — baseline uses `top_global.parquet`, CF uses Surprise SVD (`cf_svd.joblib`), and `recommend(user_id, k, mode, candidate_pool)` is the primary interface.

## Developer workflows & commands (concrete)
- Install Python deps: `pip install -r requirements.txt` (CF training requires `scikit-surprise` and `joblib` as extras).
- Run API locally (dev): from repo root:
  - `uvicorn src.api.main:app --reload --port 8000` (uses `.env` via pydantic settings in `src/api/settings.py`).
- Run UI (dev):
  - `cd ui && npm install && npm run dev` (set `VITE_API_BASE` if API is not `http://localhost:8000`).
- Train baseline (+ optional CF):
  - `python -m src.training --interactions data/interactions.parquet --train_cf` will save a new run in `models/` and update `models/LATEST`.
  - CF training uses Surprise SVD; if missing, instruct to `pip install scikit-surprise`.
- Evaluate models:
  - `python -m src.evaluation --mode baseline|cf|auto --interactions data/interactions.parquet` (uses time-based per-user holdouts; see `src/evaluation.py`).
- Quick checks:
  - `python -m src.predictions` (prints sample recommendations when run as script).

## Project-specific conventions & patterns (explicit examples)
- Artifact pointer: `models/LATEST` contains the path to the latest run directory. Training functions write LATEST automatically (`src/training.py::save_artifacts`).
- Data typing: scripts enforce types (`userId`, `movieId` -> int; `rating` -> float) — follow the same casting when adding new data code (`src/training.py`, `src/cf_training.py`).
- Evaluation leakage protection: when evaluating, `load_recommender(interactions_df=train_df)` should be used so `Recommender` builds "seen" from TRAIN only (avoid leakage) — see `src/evaluation.py` and `src/predictions.py::_load_user_seen`.
- Popularity baseline: Bayesian-smoothed popularity (`bayes_score`) implemented in `src/training.py::build_popularity_table` (min movie ratings default 20). Tests/experiments rely on these thresholds.
- Feedback sink: `/feedback` appends JSONL rows to `data/feedback.jsonl` (append-only, line-delimited JSON), so review this when testing feedback ingestion (`src/api/main.py::feedback`).
- Candidate pool / personalization: CF uses a candidate pool (default 2000) and re-ranks using predicted `cf_score` (see `src/predictions.py::recommend_cf`).

## Integration points & external dependencies
- BigQuery for raw source tables; configure env vars `SOURCE_PROJECT` and `SOURCE_DATASET` (see `src/config.py`). `src/preprocessing.py` uses the BigQuery client and emits viewer-safe queries.
- Optional TMDB enrichment or other enrichment scripts are separate (look for any `build_artifacts` or `data_enrichement` utilities if present).
- Frontend / backend contract: keep `RecommendRequest` / `RecommendResponse` sync between `src/api/schemas.py` and `ui` types (see `ui/src/lib/api.ts` and `src/api/schemas.py`).

## Helpful gotchas for agents
- Missing artifact guardrails: many runtime functions expect artifacts under `models` and `data` — create or run `src.training` to generate them before invoking the API or predictions.
- CF training requires `scikit-surprise` and can be large; `--train_cf` is optional and slower.
- Some stubbed LLM components exist under `src/llm/` (empty placeholders for `intent_parser.py`, `prompts.py`, `reranker.py`) — don't rely on them as implemented.
- Code often assumes execution from the repository root; watch for relative paths (e.g., `Path('models')` and `Path('data')`).

## When changing model-serving behavior / endpoints
- Prefer updating `src/predictions.py` and `src/api/schemas.py` and add tests (there are currently no tests — when adding, place them under `tests/`).
- Keep artifacts backward-compatible (new run folders with same artifact names are expected by `Recommender`).


## Bug Fixing & Debugging Strategy
- **Environment Context:** Always check if `.env` matches `src/api/settings.py` when an API error occurs.
- **Data Integrity:** If `Recommender` fails, check if `models/LATEST` points to a valid directory and that `.parquet` files are not empty.
- **Traceability:** When fixing a bug in `src/predictions.py`, print the shape of dataframes at each step to trace where data is lost or corrupted.
- **Logs:** Backend logs are available via the `uvicorn` console; look for `422 Unprocessable Entity` to debug schema mismatches between `src/api/schemas.py` and the UI.

## UI & API Integration (Strict Rules)
- **Type Safety:** Any change to `src/api/schemas.py` MUST be reflected in `ui/src/lib/api.ts`. The AI should verify both files before committing.
- **UI Feedback:** When adding features to `ui/`, always handle "Loading" and "Error" states for API calls using the patterns in `ui/src/components`.
- **Base URL:** Ensure the frontend uses `import.meta.env.VITE_API_BASE` for all calls; never hardcode `localhost:8000` inside components.
- **New Endpoints:** To add a feature: 
  1. Define the Pydantic schema in `src/api/schemas.py`.
  2. Implement the logic in `src/predictions.py`.
  3. Add the route in `src/api/main.py`.
  4. Update the frontend fetcher in `ui/src/lib/api.ts`.

## Endpoint Reliability & Testing
- **Validation:** Use `pydantic` types strictly. Do not bypass validation with generic `dict` or `Any`.
- **Manual Verification:** After modifying an endpoint, use the `docs` (Swagger) at `http://localhost:8000/docs` to test the payload format.
- **Regression:** If `src.training` is updated, the agent must verify that the `/recommend` endpoint still correctly loads the new artifacts via `load_recommender()`.

---
If you want, I can open a PR with this draft, refine any section with more examples (e.g. sample `uvicorn` command, a minimal end-to-end playbook), or merge into an existing `.github/copilot-instructions.md` if you have an earlier version to preserve. What should I adjust or expand? 👇
