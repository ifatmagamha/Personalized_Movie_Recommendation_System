# 🎬 Personalized Movie Recommendation System

A production-ready, hybrid recommendation engine combining Collaborative Filtering (SVD), Bayesian Popularity Ranking, and Large Language Models (LLM) for natural language intent parsing.

---

## 1. Business Objective 🎯
The goal is to solve the **"Choice Paralysis"** problem in streaming.
- **Why**: Users spend more time scrolling than watching.
- **Solution**: A system that understands *context* ("I want to cry", "Date night") via LLM and combines it with *personal taste* (CF) to deliver highly relevant suggestions instantly.
- **Value**: Increased user engagement, reduced churn, and higher session times.

---

## 2. Data Availability & Quality 📊
The system is built on the **MovieLens** ecosystem, enriched with modern metadata.

- **Primary Source**: MovieLens 100k (simulated via BigQuery/Parquet).
    - `ratings`: User-item interactions (1-5 scale).
    - `movies`: Titles and genres.
- **Enrichment**:
    - **Posters & Backdrops**: Fetched via TMDB API for a premium UI.
    - **Data Quality**: 
        - Filtered for users with >5 ratings (active users).
        - Filtered for movies with >20 ratings (statistical significance).
        - Implicit feedback (swipes) is captured for future training.

---

## 3. Success Metrics 📈

### Technical Metrics
- **Root Mean Squared Error (RMSE)**: < 0.90 on the SVD model.
- **LLM Intent Accuracy**: > 85% for Mood detection (Verified: **87.5%**).
- **Genre Recall**: > 90% mapping natural language to database genres (Verified: **92.9%**).

### Business Metrics
- **Click-Through Rate (CTR)**: Modeled via "Swipe Right" actions.
- **Session Success**: Percentage of sessions ending in a "Helpful" vote or "Watch" action.
- **Latency**: Core recommendation API response < 200ms.

---

## 4. Costs & Constraints 💰

### Constraints
- **Cold Start**: Addressed via Bayesian Popularity baseline for new users.
- **Data Cutoff**: The dataset ends in 2015; the LLM is prompted to handle "recent" queries gracefully.
- **Latency**: Real-time inference required; complex re-ranking is cached or limited to top-k candidates.

### Cost Driver
- **Compute**: Low. Runs on a standard Python 3.10 container (~500MB RAM).
- **Storage**: < 1GB for dataset and models (efficient Parquet format).
- **LLM**: Uses **Gemini 1.5 Flash** (Low cost, high speed) only for intent parsing, not for per-user ranking.

---

## 5. Model Usage & Deployment 🚀

### Architecture (Hybrid)
1.  **Candidate Generation**:
    - **SVD (Surprise)**: For personalized, user-history based scoring.
    - **Bayesian Average**: For global popularity (fallback).
2.  **Filtering Layer (LLM)**:
    - **Google Gemini 1.5 Flash**: Parses queries ("Something scary from the 90s") into structured JSON filters (`{"mood": "tense", "year": [1990, 1999], "genre": "Horror"}`).
3.  **Deployment**:
    - **Backend**: FastAPI (Python) served via Uvicorn.
    - **Frontend**: React (Vite) + Tailwind CSS.
    - **Evaluator**: Automated LLMOps dashboard for monitoring prompt performance.
    - **Infrastructure**: Fully **Dockerized** with Nginx acting as a reverse proxy for the UI.

### Running the Project
```bash
# 1. Build and Deploy
./scripts/deploy.ps1  # Windows
./scripts/deploy.sh   # Linux/Mac

# 2. Access
# UI: http://localhost
# API: http://localhost:8000
# Dashboard: http://localhost/dashboard.html
```

---

## 6. Future Perspectives & Roadmap 🔮

### Near-Term Iterations
1.  **Feedback Loop**: Implement an automated "Harvester" to retrain the SVD model nightly on new `feedback.jsonl` data.
2.  **RAG Integration**: Use Vector Search (ChromaDB) on movie plot summaries to allow semantic search ("movies about time travel paradoxes") beyond just genres.
3.  **Deployment**: Push to **Vercel** (Frontend) and **Railway/GCP** (Backend) for public access.

### Long-Term Vision
- **Multi-Modal Personalization**: Analyze movie posters using Vision Models to recommend based on visual aesthetics.
- **Online Learning**: Switch to `River` for incremental model updates instead of batch retraining.

---

## 7. Key Takeaways 🎓
- **LLMs as Selectors, Not Rankers**: It is far more efficient to use LLMs to *understand* what the user wants (filtering) than to ask them to *rank* 1000 items (scoring).
- **Hybrid is King**: Neither pure Collaborative Filtering (fails on cold start) nor pure Rules (fails on nuance) gives a complete experience. Combining them covers all bases.
- **Observability Matters**: Because LLMs are non-deterministic, having an "LLMOps Dashboard" with specific unit tests (like "I want to cry" → "Drama") is essential for preventing regressions in production.