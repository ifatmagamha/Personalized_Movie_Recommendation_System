# Personalized Movie Recommendation System
**Project Context & Technical Overview**

---

## 1. Project Overview

This project is a **full-stack personalized movie recommendation platform** that helps users discover films when they do not know what to watch.

The system combines:
- classical recommender systems (baseline + collaborative filtering),
- enriched movie metadata (TMDB),
- a modern, mood-driven swipe-based UI,
- a modular FastAPI backend,
- and a clear path toward LLM-powered intent understanding and explainability.

The guiding principle is:
> **Functional prototype first — no over-engineering, clear data flow, stable contracts.**

---

## 2. High-Level Objectives

### Core Objectives (MVP)
- Provide **movie recommendations** based on:
  - user mood / free-text intent,
  - optional filters (genres, rating),
  - optional personalization (collaborative filtering).
- Display results in a **card-swipe UI** with rich metadata (poster, description, rating).
- Collect **user feedback** to improve future recommendations.

### Secondary Objectives (Planned)
- Integrate **LLM-based intent parsing & explanation**.
- Improve recommendation logic with **hybrid ranking**.
- Add **LLMOps / MLOps** practices (versioning, monitoring).
- Containerize and document the full system.

---

## 3. Repository Structure

Personalized_Movie_Recommendation_System/
│
├── data/                     # Datasets & enriched artifacts
│   ├── movies.parquet
│   ├── movies_enriched.parquet
│   ├── interactions.parquet
│   ├── movie_stats.parquet
│   └── tmdb_mapping.parquet
│
├── build_artifacts/           # Generated / runtime artifacts
│   ├── feedback.jsonl
│   └── (future: models, indexes)
│
├── src/
│   ├── api/                   # FastAPI backend
│   │   ├── [main.py](http://main.py/)
│   │   ├── [schemas.py](http://schemas.py/)
│   │   ├── [deps.py](http://deps.py/)
│   │   ├── [filters.py](http://filters.py/)
│   │   └── [settings.py](http://settings.py/)
│   │
│   ├── build_artifacts/       # Offline data enrichment
│   │   └── enrich_tmdb.py
│   │
│   ├── [preprocessing.py](http://preprocessing.py/)
│   ├── [training.py](http://training.py/)
│   ├── cf_training.py
│   ├── [predictions.py](http://predictions.py/)
│   └── [evaluation.py](http://evaluation.py/)
│
├── ui/                        # Frontend (Vite + React + TS)
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── mappers.ts
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
│
├── tests/                     # API tests (pytest)
│   └── (unit & integration tests)
│
├── docs/                      # Documentation
├── [README.md](http://readme.md/)
└── PROJECT_CONTEXT.md         # ← this file

---

## 4. System Architecture

### High-Level Architecture

```

[ User ]
↓
[ React UI ]
↓ HTTP (JSON)
[ FastAPI Backend ]
↓
[ Recommendation Engine ]
↓
[ Enriched Movie Data + Models ]

---

## 5. Backend (API) Architecture

### Key Endpoints

| Endpoint        | Method | Purpose |
|-----------------|--------|---------|
| `/health`       | GET    | Service health check |
| `/genres`       | GET    | List available genres |
| `/recommend`    | POST   | Get movie recommendations |
| `/feedback`     | POST   | Store user feedback |

### Design Principles
- **Stateless API**
- **Explicit schemas (Pydantic)**
- **Graceful fallback** when ML artifacts are missing
- **UI-safe responses** (optional fields allowed)

### Recommendation Flow (`/recommend`)
1. Receive `RecommendRequest`
2. Select recommender:
   - `baseline`
   - `cf`
   - `auto` (default)
3. Generate ranked candidates
4. Return enriched movie objects compatible with UI

---

## 6. Data & Artifacts

### Core Datasets
- `movies.parquet`: raw MovieLens-style data
- `interactions.parquet`: user ratings
- `movie_stats.parquet`: aggregated stats

### Enriched Dataset
- `movies_enriched.parquet` (generated via TMDB)
  - poster
  - backdrop
  - description
  - duration
  - rating
  - release year

### Enrichment Strategy
- Offline batch job (`enrich_tmdb.py`)
- Stable `movieId → tmdb_id` mapping
- No overrides on re-runs
- Rate-limit safe

---

## 7. Frontend (UI) Architecture

### Stack
- React + TypeScript
- Vite
- Tailwind CSS
- Motion (Framer Motion-compatible)

### Key Design Rules
- **Design driven by Figma (locked)**
- No local fake datasets (`movies.ts` removed)
- UI consumes API only
- Optional fields handled safely

### Data Flow
User Action
→ App.tsx
→ lib/api.ts
→ Backend (/recommend)
→ mapMovieRecToUI
→ UI Components


### Stack 
python
react
you can check the requirements.txt file
