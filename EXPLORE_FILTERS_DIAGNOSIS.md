# Explore Filters Integration Diagnosis

## Current State Analysis

### ✅ What's Working (Code Review)

1. **Frontend Component (`ExploreFilters.tsx`)**
   - ✅ Calls `listGenres()` on mount via `useEffect`
   - ✅ Displays loading state while fetching
   - ✅ Shows error state with retry button
   - ✅ Renders genre buttons with include/exclude states
   - ✅ Calls `onApplyFilters(filters)` when "Apply" clicked

2. **API Integration (`ui/src/lib/api.ts`)**
   - ✅ `listGenres()` fetches from `${API_BASE}/genres`
   - ✅ Returns `data.genres ?? []`
   - ✅ Error handling with status check

3. **Backend Endpoint (`src/api/main.py`)**
   - ✅ `/genres` endpoint exists
   - ✅ Reads from `r.movies` (movies_enriched.parquet)
   - ✅ Splits genres by "|" delimiter
   - ✅ Returns `{"genres": sorted(all_genres)}`

4. **Filter Application (`App.tsx`)**
   - ✅ `handleApplyFilters()` calls `recommend()` with constraints
   - ✅ Uses same `mapMovieRecToUI()` as mood input
   - ✅ Navigates to results screen

5. **Backend Filtering (`src/api/main.py` + `src/api/filters.py`)**
   - ✅ `apply_filters()` handles genre include/exclude
   - ✅ Rating and popularity filters work
   - ✅ Enrichment happens via `_enrich()` (same as mood flow)

### ❓ Potential Issues (Need Validation)

1. **API_BASE Configuration**
   - Frontend uses: `import.meta.env.VITE_API_BASE ?? "http://localhost:8000"`
   - Backend runs on: `127.0.0.1:8000`
   - **Potential mismatch**: `localhost` vs `127.0.0.1` (usually same, but verify)

2. **Genre Loading Failure**
   - If `/genres` returns empty array or fails, `availableGenres` stays `[]`
   - Component shows empty genre list (no error visible if silent failure)
   - **Need to verify**: Is backend actually returning genres?

3. **Enrichment Source**
   - Backend loads `movies_enriched.parquet` in `Recommender.__init__()`
   - If file missing or empty, `r.movies` is `None`
   - `/genres` returns `{"genres": []}` if `r.movies is None`
   - **Need to verify**: Does `data/movies_enriched.parquet` exist and have genres?

4. **Filter Application**
   - `handleApplyFilters()` uses same flow as `handleMoodSubmit()`
   - Should work identically if backend is accessible
   - **Need to verify**: Are filtered results actually enriched?

---

## Required Information to Diagnose

### 1. Backend Endpoint Response
**Why needed**: Verify backend is returning genres correctly

**What to provide**:
```bash
# Test genres endpoint
curl http://127.0.0.1:8000/genres

# Expected: {"genres": ["Action", "Adventure", ...]}
# If empty: Backend can't read movies_enriched.parquet
```

**What it validates**:
- Backend can access `movies_enriched.parquet`
- Genres are extracted correctly
- Endpoint is accessible from frontend

---

### 2. Frontend Browser Console
**Why needed**: Check if API calls are failing silently

**What to provide**:
- Open browser DevTools → Console tab
- Navigate to Explore Filters screen
- Check for:
  - `GET http://localhost:8000/genres` requests
  - Any CORS errors
  - Any network errors (404, 500, etc.)
  - Console errors from `listGenres()` catch block

**What it validates**:
- API calls are being made
- CORS is configured correctly
- Error handling is working

---

### 3. Backend Logs
**Why needed**: Verify backend is processing requests

**What to provide**:
- Backend terminal output when:
  - Frontend calls `/genres`
  - Frontend calls `/recommend` with filters
- Look for:
  - `[INFO] Loading enriched movies from data/movies_enriched.parquet`
  - `[INFO] Enrichment source loaded: X movies available`
  - Any errors about missing files

**What it validates**:
- Backend is receiving requests
- Enrichment source is loaded
- No file access errors

---

### 4. Data File Verification
**Why needed**: Ensure source data exists

**What to provide**:
```python
# Run in Python (if available)
import pandas as pd
from pathlib import Path

p = Path("data/movies_enriched.parquet")
print(f"Exists: {p.exists()}")
if p.exists():
    df = pd.read_parquet(p)
    print(f"Rows: {len(df)}")
    print(f"Has genres: {'genres' in df.columns}")
    if 'genres' in df.columns:
        print(f"Sample genres: {df['genres'].head(5).tolist()}")
```

**What it validates**:
- `movies_enriched.parquet` exists
- Contains `genres` column
- Has data to extract genres from

---

### 5. Network Request Details
**Why needed**: Verify request/response format matches

**What to provide**:
- Browser DevTools → Network tab
- Filter by "genres" or "recommend"
- Click on request → Check:
  - Request URL (should be `http://localhost:8000/genres`)
  - Request Method (GET for genres, POST for recommend)
  - Response Status (200 = success)
  - Response Body (JSON with genres array)

**What it validates**:
- Request format is correct
- Response format matches expected schema
- No HTTP errors

---

## Integration Flow (Expected)

```
1. User navigates to Explore Filters
   └─> ExploreFilters component mounts
       └─> useEffect triggers loadGenres()
           └─> listGenres() calls GET /genres
               └─> Backend reads movies_enriched.parquet
                   └─> Extracts unique genres
                       └─> Returns {"genres": [...]}
                           └─> Frontend sets availableGenres state
                               └─> UI renders genre buttons

2. User selects filters and clicks "Apply"
   └─> handleApply() calls onApplyFilters(filters)
       └─> App.tsx handleApplyFilters() called
           └─> recommend() POST /recommend with constraints
               └─> Backend: r.recommend() → model inference
                   └─> Backend: apply_filters() → genre/rating filters
                       └─> Backend: _enrich() → merge with movies_enriched
                           └─> Returns enriched recommendations
                               └─> Frontend: mapMovieRecToUI()
                                   └─> setRecommendedMovies()
                                       └─> Navigate to ResultsScreen
```

---

## Potential Root Causes

### Scenario A: Genres Not Loading
**Symptoms**: Empty genre list, no error shown
**Possible causes**:
1. Backend not running or inaccessible
2. `movies_enriched.parquet` missing or empty
3. CORS blocking request
4. API_BASE mismatch (localhost vs 127.0.0.1)

**Fix strategy**:
- Verify backend is running on `127.0.0.1:8000`
- Check `data/movies_enriched.parquet` exists
- Verify CORS allows frontend origin
- Check browser console for network errors

---

### Scenario B: Genres Load But Filtered Results Empty
**Symptoms**: Genres display, but "Apply" shows no movies
**Possible causes**:
1. Filter constraints too strict (no matches)
2. Enrichment failing silently
3. `apply_filters()` returning empty DataFrame

**Fix strategy**:
- Check backend logs for enrichment warnings
- Verify filter logic in `apply_filters()`
- Test with minimal filters (no genres, low rating)

---

### Scenario C: Filtered Results Show But Missing Posters
**Symptoms**: Movies display but show "No poster" placeholder
**Possible causes**:
1. Enrichment merge failing (movieId mismatch)
2. `poster` column missing from movies_enriched.parquet
3. Poster URLs are null/empty in source data

**Fix strategy**:
- Check backend logs: `[WARN] _enrich: only X/Y movies have poster`
- Verify `movies_enriched.parquet` has `poster` column
- Check sample poster URLs in parquet file

---

## Safe Integration Strategy

### Step 1: Verify Backend Accessibility
```typescript
// Add to ExploreFilters.tsx temporarily for debugging
useEffect(() => {
  // Test backend connection
  fetch('http://127.0.0.1:8000/health')
    .then(r => r.json())
    .then(data => console.log('Backend health:', data))
    .catch(err => console.error('Backend unreachable:', err));
  
  loadGenres();
}, []);
```

### Step 2: Add Genre Loading Debugging
```typescript
const loadGenres = () => {
  setLoading(true);
  console.log('[ExploreFilters] Fetching genres from:', API_BASE);
  listGenres()
    .then((g) => {
      console.log('[ExploreFilters] Received genres:', g?.length || 0);
      setAvailableGenres(g ?? []);
      setError(null);
    })
    .catch((err) => {
      console.error('[ExploreFilters] Genre fetch failed:', err);
      setError("Failed to load genres");
    })
    .finally(() => setLoading(false));
};
```

### Step 3: Verify Filter Application
```typescript
// Add to App.tsx handleApplyFilters
console.log('[App] Applying filters:', filters);
console.log('[App] API request:', {
  mode: filters.isPersonalized ? "cf" : "baseline",
  constraints: {
    genres_in: filters.selectedGenres,
    genres_out: filters.excludedGenres,
    min_avg_rating: filters.minRating,
  }
});
```

---

## Validation Checklist

Once you provide the requested information, I can validate:

- [ ] Backend `/genres` endpoint returns genres array
- [ ] Frontend `listGenres()` receives and stores genres
- [ ] Genre buttons render in UI
- [ ] Filter application calls `/recommend` with correct constraints
- [ ] Backend `apply_filters()` processes constraints correctly
- [ ] Enrichment merges poster/description from movies_enriched.parquet
- [ ] Results display with correct posters and metadata
- [ ] No regression in mood input → results flow
- [ ] No regression in swipe refinement logic

---

## Next Steps

**Please provide**:
1. Output of `curl http://127.0.0.1:8000/genres` (or equivalent)
2. Browser console errors/warnings when loading Explore Filters
3. Backend terminal logs when accessing Explore Filters
4. Network tab screenshot showing `/genres` request/response
5. Confirmation that `data/movies_enriched.parquet` exists

With this information, I can:
- Identify the exact failure point
- Provide targeted fixes
- Ensure no regression in existing flows
- Validate end-to-end integration
