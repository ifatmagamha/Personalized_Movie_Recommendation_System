# End-to-End System Workflow

## 1. Flow Overview

### A. Mood Search (LLM-Led)
1. User enters: "I want a dark 80s thriller".
2. LLM (`gemini-flash-latest`) extracts: `Horror`, `Thriller`, `min_year: 1980`.
3. Recommender filters top 2000 movies and returns top 8 matches.
4. LLM narrates why each movie fits the "dark" vibe.

### B. Personalization (Feedback-Led)
1. User swiped 3+ movies as "Like".
2. UI detects `swipedCount >= Threshold`.
3. Backend switches to `mode: cf`.
4. SVD model scores the filtered candidate pool.
5. Next batch of 8 cards shows personalized predicted hits.

## 2. Technical Decision Logic

| Component | Logic | Target |
| :--- | :--- | :--- |
| **Model Selection** | If History > 3 Likes then CF else Baseline | Best relevancy |
| **Candidate Pool** | Global Top 2000 | Quality filtering |
| **Enrichment** | TMDB metadata merged BEFORE filtering | Dynamic accuracy |
| **Swipe Logic** | Trigger refinement when 2 cards remain | Finite browsing |

## 3. Deployment & MLOps Readiness
- **Prompt Isolation**: Prompts in `src/llm/prompts.py` can be tuned without code changes.
- **Model Reloading**: `/admin/reload` allows updating SVD models hot.
- **Enrichment Source**: `data/movies_enriched.parquet` is the definitive source for UI assets.

## 4. Visualization Walkthrough (Testing the Fixes)

To observe the system's dynamic behaviors, follow these steps:

### A. Run the Environment
1. **Server**: `.\venv\Scripts\python.exe -m src.api.main`
2. **UI**: `npm run dev` (inside `/ui`)

### B. Test Scenarios
- **Filter Precision**: Open the "Explore Favorites" screen. Select a specific genre (e.g., "Western"). Notice how the 8 cards refresh instantly with only Westerns, including high-quality metadata like posters and ratings.
- **Mood Intent**: Go to the "Mood Search" screen and type "I want to watch something exciting from the 90s".
  - **Verification**: The results should be filtered to 1990-1999 and include Action/Thriller genres.
  - **Check Reasons**: Each card should have a "Personalized Reason" explaining why it matches that specific mood.
- **Finite Batching**: Swipe through the cards. Notice that the deck is finite (8 cards). When you reach the last 2 cards, the system intelligently fetches a new batch based on your likes.

### C. MLOps Monitoring
- **Admin**: Visit `http://localhost:8000/docs` to test the `/admin/reload` endpoint. This allows you to hot-swap models without restarting the server.
- **Interactions**: Check `data/feedback.jsonl` after swiping. You will see raw logs of every action, ready for the next training cycle.
