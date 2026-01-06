# Recommendation Flow Diagnosis & Fixes

## Executive Summary

Fixed critical issues in the end-to-end recommendation flow:
1. **Backend accessibility**: Changed host from `0.0.0.0` to `127.0.0.1` for browser access
2. **Enrichment validation**: Added logging and validation to ensure poster/description are properly merged
3. **Column selection**: Fixed `recommend_baseline()` and `recommend_cf()` to include all enriched fields (poster, description, etc.)
4. **Swipe refinement**: Implemented automatic recommendation refinement when user swipes near end of list
5. **Data mapping**: Improved mapper to handle empty/null poster strings

---

## Diagnosis

### Issue 1: Backend Not Accessible
**Problem**: Backend configured to run on `0.0.0.0:8000`, which browsers cannot access directly.
- **Error**: `ERR_ADDRESS_INVALID` when accessing `http://0.0.0.0:8000`
- **Root cause**: `0.0.0.0` is a bind-all address for servers, not a client-accessible URL
- **Fix**: Changed to `127.0.0.1` (localhost) in `src/api/main.py`

### Issue 2: Movie Cards Showing "No Poster"
**Problem**: Genres render correctly, but poster/description are missing or incorrect.
- **Root cause**: 
  - `_enrich()` method performs left merge but doesn't validate success
  - `recommend_baseline()` and `recommend_cf()` select columns BEFORE enrichment completes, excluding `poster`, `description`, etc.
  - API endpoint uses `row.get()` which returns `None` for missing keys without validation
- **Fix**: 
  - Added enrichment validation and logging
  - Fixed column selection to include all enriched fields
  - Improved `_safe()` helper usage in API endpoint

### Issue 3: Cold-Start Swipe Has No Logic
**Problem**: Swipe interactions exist but don't trigger new recommendations.
- **Root cause**: `handleSwipeComplete()` only advances `currentIndex`, no refinement logic
- **Fix**: 
  - Added `swipedMovieIds` and `likedMovieIds` state tracking
  - Implemented `refineRecommendations()` that excludes swiped movies and prefers liked genres
  - Triggers automatically when 3 or fewer movies remain

---

## Data Flow (Validated)

### Current Flow (After Fixes)

```
1. User Input → API Request
   ├─ Mood input → `/recommend` with query
   └─ Filter selection → `/recommend` with constraints

2. Model Inference → Movie IDs
   ├─ `r.recommend()` returns DataFrame with movieId + scores
   ├─ Mode: baseline (popularity) or cf (collaborative filtering)
   └─ Output: DataFrame with columns: [movieId, score, ...]

3. Enrichment → Full Features
   ├─ `_enrich()` merges with `movies_enriched.parquet` on movieId
   ├─ Left join ensures all recommended IDs are kept
   ├─ Adds: poster, backdrop, description, year, rating, duration
   └─ Validation: logs enrichment success rate

4. Filtering → Apply Constraints
   ├─ `apply_filters()` filters by genres, rating, excludes
   └─ Falls back to base_df if filter results empty

5. API Response → JSON
   ├─ Extracts fields using `_safe()` helper (handles NaN/None)
   ├─ Returns: {movieId, title, genres, poster, description, ...}
   └─ Validation: logs missing titles/posters

6. Frontend Mapping → UI Format
   ├─ `mapMovieRecToUI()` converts API response
   ├─ Handles null/empty poster → uses FALLBACK_POSTER
   └─ Splits genres string into array

7. UI Rendering → Movie Cards
   ├─ ResultsScreen displays cards with poster, title, genres
   └─ Swipe interactions trigger refinement when near end
```

### Key Validation Points

1. **Enrichment Success**: Check backend logs for:
   - `[INFO] Enrichment source loaded: X movies available`
   - `[INFO] Enrichment check: poster=True, description=True`
   - `[WARN] _enrich: only X/Y movies have poster` (if issues)

2. **API Response Quality**: Verify each recommendation has:
   - Valid `movieId` (integer)
   - Non-empty `title`
   - `poster` URL (or fallback in UI)
   - `genres` (string, split in frontend)

3. **Swipe Refinement**: Check that:
   - Swiping through 10+ movies triggers new recommendations
   - Swiped movies are excluded from new batch
   - Liked genres influence new recommendations

---

## Files Modified

### Backend
1. **`src/api/main.py`**
   - Changed host from `0.0.0.0` to `127.0.0.1`
   - Added enrichment validation logging
   - Improved `_safe()` usage for all optional fields
   - Added title validation with fallback

2. **`src/predictions.py`**
   - Enhanced `_enrich()` with validation and logging
   - Fixed `recommend_baseline()` to include all enriched columns
   - Fixed `recommend_cf()` to include all enriched columns

### Frontend
3. **`ui/src/app/App.tsx`**
   - Added `swipedMovieIds` and `likedMovieIds` state
   - Implemented `refineRecommendations()` function
   - Added `handleSwipeAction()` with refinement logic
   - Updated ResultsScreen props to pass refinement flag

4. **`ui/src/app/components/ResultsScreen.tsx`**
   - Updated `handleSwipeComplete()` to trigger refinement
   - Calculates remaining movies and sets `shouldRefine` flag

5. **`ui/src/lib/mappers.ts`**
   - Improved poster handling (empty string → fallback)
   - Added title fallback for missing titles

---

## Must-Keep Logic

### Backend
- ✅ `_enrich()` left merge on `movieId` (preserves all recommendations)
- ✅ `apply_filters()` genre/rating filtering (user constraints)
- ✅ `_safe()` helper for null/NaN handling (data safety)
- ✅ Fallback to `base_df` if filters empty (prevents empty results)

### Frontend
- ✅ `mapMovieRecToUI()` fallback handling (UI safety)
- ✅ Genre splitting logic (handles pipe/comma delimited)
- ✅ Swipe UI interactions (user experience)

---

## Broken/Missing Logic (Now Fixed)

### Backend
- ❌ **FIXED**: Enrichment validation (was silent failures)
- ❌ **FIXED**: Column selection excluding enriched fields
- ❌ **FIXED**: No logging for debugging enrichment issues

### Frontend
- ❌ **FIXED**: Swipe refinement (was static array only)
- ❌ **FIXED**: Empty poster string handling
- ❌ **FIXED**: No state tracking for swiped/liked movies

---

## Validation Steps

### 1. Backend Enrichment
```bash
# Start backend
cd <project_root>
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# Check logs for:
# [INFO] Loading enriched movies from data/movies_enriched.parquet
# [INFO] Enrichment source loaded: X movies available
# [INFO] Enrichment check: poster=True, description=True
```

### 2. API Response Validation
```bash
# Test recommendation endpoint
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"k": 5, "mode": "baseline"}'

# Verify response includes:
# - movieId (integer)
# - title (non-empty string)
# - poster (URL or null)
# - genres (string)
```

### 3. Frontend Rendering
1. Start frontend: `cd ui && npm run dev`
2. Navigate to Explore Filters
3. Apply filters → Check ResultsScreen
4. Verify:
   - Posters display (not "No poster" placeholder)
   - Titles match genres
   - Metadata (year, rating) visible

### 4. Swipe Refinement
1. Swipe through 10+ movies
2. Check browser console for API calls when 3 movies remain
3. Verify new movies appear (not duplicates)
4. Verify swiped movies are excluded

---

## Testing Checklist

- [ ] Backend starts on `http://127.0.0.1:8000`
- [ ] `/health` endpoint returns `{"status": "ok"}`
- [ ] `/recommend` returns recommendations with posters
- [ ] Frontend loads genres from `/genres` endpoint
- [ ] Filter-based recommendations show correct posters
- [ ] Swipe interactions advance through movies
- [ ] Swipe refinement triggers when 3 movies remain
- [ ] New recommendations exclude already-swiped movies
- [ ] Liked genres influence new recommendations

---

## Notes

- **Enrichment Source**: `data/movies_enriched.parquet` must exist and contain `poster`, `description`, etc.
- **Model Artifacts**: If `models/LATEST` doesn't exist, system runs in DATA-ONLY mode (uses movies_enriched as baseline)
- **Fallback Behavior**: If enrichment fails, recommendations still return but with missing metadata (UI shows fallbacks)
- **Swipe Refinement**: Only triggers in "results" screen, requires at least 3 initial recommendations

---

## Next Steps (Optional Enhancements)

1. **Caching**: Cache enriched movies in memory to avoid repeated parquet reads
2. **Batch Refinement**: Pre-fetch next batch before user reaches end
3. **Genre Extraction**: Improve genre extraction from liked movies (weight by frequency)
4. **Error Recovery**: Retry enrichment if merge fails for specific movieIds
5. **Metrics**: Track enrichment success rate, refinement triggers, user engagement
