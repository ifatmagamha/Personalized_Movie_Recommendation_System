
# UI–Backend Integration Traceability

## 1. Summary of Recent Fixes

### A. Backend Validation Fix (Duplicate Columns)
*   **Issue**: Movies in the UI were missing posters and titles, despite data existing.
*   **Root Cause**: The `_enrich` method in `src/predictions.py` blindly merged the `movies` dataframe. Since both the recommendation dataframe and enrichment dataframe had `title` columns, pandas created `title_x` and `title_y`, leaving the critical `title` column undefined (NaN).
*   **Fix**: Modified `_enrich` to explicitly calculate and merge ONLY the difference in columns (`cols_to_add`).
*   **Impact**: UI now correctly renders all movie metadata.

### B. Cold Start "Infinite Loop / Empty State"
*   **Issue**: Users swiped 3-4 times and hit an empty "That's all for now" screen, forcing a manual reset.
*   **Root Cause**:
    1.  Initial batch size `k=12` was too small for rapid swiping.
    2.  No logic existed to fetch *more* movies when the stack ran low.
*   **Fix**:
    1.  Increased `k` to 48 in `App.tsx`.
    2.  Implemented `handleSwipeAction` with a "Refine" trigger: when `<3` movies remain, the frontend automatically requests a new batch, excluding already swiped IDs.

### C. Explore Filters (3-State Logic)
*   **Issue**: Filter logic was brittle; "Included" vs "Excluded" was not clearly distinguished in state.
*   **Fix**: Rewrote `ExploreFilters.tsx` to use a robust 3-state cycle (Neutral -> Include -> Exclude) and mapped the `minPopularity` slider to the backend's `min_n_ratings` parameter.

## 2. Technical Contracts

### API Contracts
*   **`POST /recommend`**:
    *   **Input**: `constraints: { genres_in: [...], exclude_movieIds: [...] }`
    *   **Output**: `recommendations: [ { movieId, title, poster, ... }, ... ]`
    *   **Guarantee**: Output objects are fully hydrated. No `_x` suffixes.

### Data Contracts
*   **`movies_enriched.parquet`**:
    *   Must contain `movieId` (int), `title` (str), `poster` (str/url).
    *   Used as the fallback Source of Truth if model artifacts are missing.

## 3. Validation Steps (Regression Testing)

To verify system integrity after any future changes:

1.  **Check Enrichment**:
    *   Run `python -m src.api.main` (or test script).
    *   Ensure `POST /recommend` returns `poster` fields that are not null.

2.  **Check Cold Start**:
    *   Fresh load of UI.
    *   Swipe right 20 times.
    *   Verify no empty state is reached prematurely.

3.  **Check Filters**:
    *   Select "Horror" (Exclude).
    *   Verify results contain NO horror movies.

## 4. Open Risks / Follow-ups
*   **Filter Strictness**: If a user excludes too many genres, `k=48` might result in `<48` actual movies if the candidate pool (2000) is exhausted.
*   **Performance**: `pd.merge` in `_enrich` is fast for 50 items but `pd.read_parquet` on every startup is slow. `lru_cache` mitigates this for now.
