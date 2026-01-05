# Maybe This - Screen Flow Documentation

## Overview

OFF Hours uses a **5-screen flow** with an **overlay modal** for movie details. The app implements an emotion-first discovery experience with two recommendation paths: AI-powered mood parsing and manual filter exploration.

---

## Screen Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    App State Layer                      │
│  - currentScreen: 'home' | 'mood-input' | 'explore-    │
│    filters' | 'quick-recommend' | 'results'             │
│  - selectedMovie: Movie | null (for modal)              │
│  - moodInput: string (user's mood text)                 │
│  - isVoiceInput: boolean (text vs voice)                │
│  - recommendedMovies: Movie[] (filtered results)        │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Screen Flow Map

```
┌──────────────────┐
│   1. HOME        │ (Entry Point)
│  "Maybe THIS."   │
└────────┬─────────┘
         │
         ├─────────────────────────┬──────────────────────┐
         │                         │                      │
         ▼                         ▼                      ▼
┌────────────────┐      ┌──────────────────┐   ┌──────────────────┐
│ 2. MOOD INPUT  │      │ 3. EXPLORE       │   │ 4. QUICK         │
│ Text/Voice     │      │    FILTERS       │   │    RECOMMEND     │
│ Emotion Parser │      │ Genre + Sliders  │   │ (Top Rated)      │
└───────┬────────┘      └─────────┬────────┘   └────────┬─────────┘
        │                         │                      │
        │  (AI Processing)        │  (Filter Logic)      │ (Direct)
        │                         │                      │
        └─────────────────────────┴──────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  5. RESULTS      │
                         │  Swipe Cards     │
                         │  Like/Dislike    │
                         └────────┬─────────┘
                                  │
                                  │ (Tap card)
                                  ▼
                         ┌──────────────────┐
                         │  MOVIE DETAIL    │
                         │  (Modal Overlay) │
                         │  Full Info       │
                         └──────────────────┘
```

---

## Screen-by-Screen Details

### 1. HOME SCREEN
**File:** `/src/app/components/HomeScreen.tsx`

#### Purpose
Landing page with branding and entry points to recommendation systems.

#### Visual Design
- Dark background (neutral-950) with neon accent glows
- "(Maybe THIS.)" branding with pink accent
- Minimalist, centered layout
- Subtle pulsing background effects (pink/blue/purple)

#### User Actions
| Action | Triggers | Navigation |
|--------|----------|------------|
| Click "tell us how you're feeling" | `onMoodInput()` | → Mood Input Screen |
| Click "i just need something" | `onQuickRecommend()` | → Explore Filters Screen |

#### Props Interface
```typescript
interface HomeScreenProps {
  onQuickRecommend: () => void;
  onMoodInput: () => void;
}
```

#### State Changes
```typescript
// When user clicks mood input
onMoodInput={() => setCurrentScreen('mood-input')}

// When user clicks quick recommend
onQuickRecommend={() => setCurrentScreen('explore-filters')}
```

#### Data Flow
**IN:** None (entry point)  
**OUT:** None (just navigation triggers)

---

### 2. MOOD INPUT SCREEN
**File:** `/src/app/components/MoodInput.tsx`

#### Purpose
Capture user's emotional state through text or voice input for AI-powered recommendations.

#### Visual Design
- Dark background with neon accent
- Large textarea for text input
- Microphone button for voice input
- Placeholder prompts: "feeling lonely at 3am...", "can't sleep, need something quiet", etc.
- Back arrow in top-left

#### User Actions
| Action | Triggers | Navigation |
|--------|----------|------------|
| Type mood text + Submit | `onSubmit(text, false)` | → Results Screen |
| Click microphone + speak | `onSubmit(transcript, true)` | → Results Screen |
| Click back arrow | `onBack()` | → Home Screen |

#### Props Interface
```typescript
interface MoodInputProps {
  onSubmit: (input: string, isVoice: boolean) => void;
  onBack: () => void;
}
```

#### State Changes
```typescript
// When user submits mood
handleMoodSubmit(input: string, isVoice: boolean) {
  setMoodInput(input);                    // Store mood text
  setIsVoiceInput(isVoice);               // Track input method
  const recommended = parseIntentAndRecommend(input, isVoice);
  setRecommendedMovies(recommended);      // AI-generated results
  setCurrentScreen('results');            // Navigate to results
}
```

#### AI Parsing Logic
The mood input goes through **intent parsing** with these patterns:

```typescript
// Example patterns detected:
"lonely at 3am" → moods: ['lonely', 'melancholic', 'contemplative']
"can't sleep" → moods: ['contemplative', 'calm', 'peaceful']
"broke up" → moods: ['sad', 'melancholic', 'reflective']
"need a laugh" → moods: ['happy', 'light', 'playful']
"feeling weird" → moods: ['curious', 'contemplative']
```

**Scoring Algorithm:**
1. Match detected moods to movie.mood array (+3 points each)
2. Match mood-to-genre mapping (+2 points each)
3. Boost highly-rated movies (+1 if rating ≥ 8.5)
4. Sort by score, return top 10 matches

#### Data Flow
**IN:**  
- None

**OUT:**  
- `moodInput` (string) - User's original text
- `isVoiceInput` (boolean) - Input method
- `recommendedMovies` (Movie[]) - AI-filtered results (top 10)

---

### 3. EXPLORE FILTERS SCREEN
**File:** `/src/app/components/ExploreFilters.tsx`

#### Purpose
Manual filter-based discovery with genre selection and rating/popularity controls.

#### Visual Design
- Dark background with neon accents
- Popular/Personalized toggle at top
- Genre chips with include (+) / exclude (-) buttons
- Two sliders: Minimum Rating (0-10) and Popularity
- "Show Results" button at bottom
- Back arrow in top-left

#### User Actions
| Action | Triggers | Result |
|--------|----------|--------|
| Toggle Popular/Personalized | Updates `isPersonalized` | Changes sorting logic |
| Click genre + button | Adds to `selectedGenres` | Include filter |
| Click genre - button | Adds to `excludedGenres` | Exclude filter |
| Adjust rating slider | Updates `minRating` | Minimum rating filter |
| Click "Show Results" | `onApplyFilters(filters)` | → Results Screen |
| Click back arrow | `onBack()` | → Home Screen |

#### Props Interface
```typescript
interface ExploreFiltersProps {
  onApplyFilters: (filters: FilterState) => void;
  onBack: () => void;
}

interface FilterState {
  selectedGenres: string[];    // Include these genres
  excludedGenres: string[];    // Exclude these genres
  minRating: number;           // Minimum rating (0-10)
  minPopularity: number;       // Popularity threshold
  isPersonalized: boolean;     // Popular vs Personalized
}
```

#### State Changes
```typescript
// When user applies filters
handleApplyFilters(filters: FilterState) {
  let filtered = [...MOVIES];

  // 1. Include selected genres
  if (filters.selectedGenres.length > 0) {
    filtered = filtered.filter(movie =>
      movie.genres.some(genre => filters.selectedGenres.includes(genre))
    );
  }

  // 2. Exclude unwanted genres
  if (filters.excludedGenres.length > 0) {
    filtered = filtered.filter(movie =>
      !movie.genres.some(genre => filters.excludedGenres.includes(genre))
    );
  }

  // 3. Apply rating filter
  filtered = filtered.filter(movie => movie.rating >= filters.minRating);

  // 4. Sort by Popular or Personalized
  if (filters.isPersonalized) {
    filtered = filtered.sort(() => Math.random() - 0.5); // Shuffle
  } else {
    filtered = filtered.sort((a, b) => b.rating - a.rating); // By rating
  }

  setRecommendedMovies(filtered.slice(0, 12));
  setMoodInput('Filtered results');
  setCurrentScreen('results');
}
```

#### Available Genres
```typescript
['Drama', 'Thriller', 'Romance', 'Horror', 'Comedy', 
 'Sci-Fi', 'Action', 'Animation', 'Documentary', 'Fantasy']
```

#### Data Flow
**IN:**  
- None

**OUT:**  
- `moodInput` = "Filtered results" (placeholder)
- `isVoiceInput` = false
- `recommendedMovies` (Movie[]) - Filtered results (up to 12)

---

### 4. QUICK RECOMMEND SCREEN
**File:** `/src/app/components/QuickRecommend.tsx`

#### Purpose
Fast baseline recommendations showing top-rated films in grid format.

#### Visual Design
- Grid layout of movie cards
- Each card shows: poster, title, year, rating
- Hover effects with neon glow
- Back button in top-left

#### User Actions
| Action | Triggers | Navigation |
|--------|----------|------------|
| Click movie card | `onSelectMovie(movie)` | → Movie Detail Modal |
| Click back arrow | `onBack()` | → Home Screen |

#### Props Interface
```typescript
interface QuickRecommendProps {
  movies: Movie[];
  onSelectMovie: (movie: Movie) => void;
  onBack: () => void;
}
```

#### State Changes
```typescript
// When user clicks a movie
onSelectMovie={(movie) => setSelectedMovie(movie)}
// Triggers MovieDetail modal to open
```

#### Data Flow
**IN:**  
- `movies` (Movie[]) - All movies from database

**OUT:**  
- `selectedMovie` (Movie) - Clicked movie for detail view

---

### 5. RESULTS SCREEN
**File:** `/src/app/components/ResultsScreen.tsx`

#### Purpose
Primary discovery interface with swipeable cards for liking/disliking movies.

#### Visual Design
- Dark background with neon accents
- Stack of cards with top card interactive
- Each card shows: poster, title, year, genres, rating
- Swipe indicators (pink heart for right, blue X for left)
- Bottom buttons: Dislike (X), Save (Bookmark), Like (Heart)
- "maybe this again" button when stack is empty

#### Card Swipe Mechanics
```typescript
// Swipe right (Like)
- Card translates right with rotation
- Pink heart indicator appears
- Card exits screen
- Shows next card

// Swipe left (Dislike)  
- Card translates left with rotation
- Blue X indicator appears
- Card exits screen
- Shows next card

// Tap card
- Opens Movie Detail modal
```

#### User Actions
| Action | Triggers | Result |
|--------|----------|--------|
| Swipe right (drag right) | Like movie | Remove from stack, track like |
| Swipe left (drag left) | Dislike movie | Remove from stack, track dislike |
| Click heart button | `handleLike()` | Same as swipe right |
| Click X button | `handleDislike()` | Same as swipe left |
| Click bookmark button | `handleSave()` | Save movie (visual feedback) |
| Click card title/poster | `onSelectMovie(movie)` | → Movie Detail Modal |
| Click back arrow | `onBack()` | → Home Screen |
| Click "maybe this again" | Reloads results | Restart stack |

#### Props Interface
```typescript
interface ResultsScreenProps {
  movies: Movie[];              // Recommended movies to show
  moodInput: string;            // Original mood text (for display)
  isVoice: boolean;             // Was it voice input?
  onSelectMovie: (movie: Movie) => void;
  onBack: () => void;
}
```

#### Internal State
```typescript
const [currentIndex, setCurrentIndex] = useState(0);     // Which card
const [savedMovies, setSavedMovies] = useState<Set<string>>(new Set());
const [likedMovies, setLikedMovies] = useState<string[]>([]);
const [dislikedMovies, setDislikedMovies] = useState<string[]>([]);
```

#### Swipe Physics
```typescript
// Drag thresholds
const swipeThreshold = 100; // px to trigger swipe

// Visual feedback
- Opacity changes based on drag distance
- Rotation increases with horizontal drag
- Heart/X indicators fade in during drag
- Card stack depth effect (3 cards visible)
```

#### End of Stack Behavior
```typescript
if (currentIndex >= movies.length) {
  // Show "maybe this again" button
  // Allows user to restart the stack
  // Returns to beginning of recommendations
}
```

#### Data Flow
**IN:**  
- `movies` (Movie[]) - Filtered/recommended movies
- `moodInput` (string) - User's original mood text
- `isVoice` (boolean) - Input method indicator

**OUT:**  
- `selectedMovie` (Movie) - For detail modal
- Implicit: Like/dislike/save data (could be sent to backend)

---

### MOVIE DETAIL MODAL (Overlay)
**File:** `/src/app/components/MovieDetail.tsx`

#### Purpose
Full movie information with save/feedback actions.

#### Visual Design
- Modal overlay with dark backdrop
- Two-column layout (desktop): poster left, info right
- Single column (mobile)
- Shows: poster, title, year, duration, director, rating, description, cast, tags, cinematography
- Action buttons: Save, Like, Dislike
- Close button (X) in top-right

#### Display Sections
```typescript
1. Header
   - Genres (pill badges)
   - Title (large)
   - Meta: Year, Duration, Director

2. Synopsis
   - Full description text

3. Cinematography
   - Visual style note (if available)

4. Cast
   - Comma-separated actor list

5. Tags
   - Movie characteristic tags

6. Actions
   - Save button
   - Like/Dislike buttons with feedback tracking
```

#### User Actions
| Action | Triggers | Result |
|--------|----------|--------|
| Click X or backdrop | `onClose()` | Close modal |
| Click Save | Toggles save state | Visual feedback |
| Click Like | `onFeedback(id, 'helpful')` | Track feedback |
| Click Dislike | `onFeedback(id, 'not-helpful')` | Track feedback |

#### Props Interface
```typescript
interface MovieDetailProps {
  movie: Movie;
  onClose: () => void;
  onFeedback?: (movieId: string, feedback: 'helpful' | 'not-helpful') => void;
}
```

#### State Changes
```typescript
// When user closes modal
onClose={() => setSelectedMovie(null)}

// When user gives feedback
onFeedback={(movieId, feedback) => {
  // Send to backend for recommendation improvement
  console.log(`Feedback for ${movieId}: ${feedback}`);
}}
```

#### Modal Behavior
- Opens when `selectedMovie !== null`
- Closes when `selectedMovie = null`
- Can be opened from: Results Screen, Quick Recommend
- Background click closes modal
- Escape key closes modal
- Prevents body scroll when open

#### Data Flow
**IN:**  
- `movie` (Movie) - Selected movie to display

**OUT:**  
- Feedback data (helpful/not-helpful)
- Save state (could persist to backend)

---

## Navigation Flow Examples

### Path 1: AI-Powered Mood Discovery
```
User Journey:
1. HOME → Click "tell us how you're feeling"
2. MOOD INPUT → Type "feeling lonely at 3am" → Submit
3. RESULTS → See 10 mood-matched movies in swipe cards
4. Swipe right on interesting ones, left on others
5. Click card to see full details
6. MOVIE DETAIL → Read synopsis, cast, save movie
```

Code Flow:
```typescript
// Step 1
<HomeScreen onMoodInput={() => setCurrentScreen('mood-input')} />

// Step 2
<MoodInput onSubmit={(input, isVoice) => {
  setMoodInput(input);
  const recommended = parseIntentAndRecommend(input, isVoice);
  setRecommendedMovies(recommended); // AI filtering happens here
  setCurrentScreen('results');
}} />

// Step 3
<ResultsScreen 
  movies={recommendedMovies}  // AI-filtered results
  moodInput={moodInput}
  onSelectMovie={(movie) => setSelectedMovie(movie)}
/>

// Step 4
<MovieDetail 
  movie={selectedMovie}
  onClose={() => setSelectedMovie(null)}
/>
```

### Path 2: Manual Filter Discovery
```
User Journey:
1. HOME → Click "i just need something"
2. EXPLORE FILTERS → Select Drama + Romance, exclude Horror
3. Set minimum rating to 8.0
4. Toggle to "Popular"
5. Click "Show Results"
6. RESULTS → Browse filtered movies in swipe interface
```

Code Flow:
```typescript
// Step 1
<HomeScreen onQuickRecommend={() => setCurrentScreen('explore-filters')} />

// Step 2-5
<ExploreFilters onApplyFilters={(filters) => {
  let filtered = MOVIES
    .filter(m => m.genres.some(g => filters.selectedGenres.includes(g)))
    .filter(m => !m.genres.some(g => filters.excludedGenres.includes(g)))
    .filter(m => m.rating >= filters.minRating)
    .sort((a, b) => b.rating - a.rating);
  
  setRecommendedMovies(filtered.slice(0, 12));
  setCurrentScreen('results');
}} />

// Step 6
<ResultsScreen movies={recommendedMovies} />
```

### Path 3: Quick Top-Rated Browse
```
User Journey:
1. HOME → Click "i just need something" (currently goes to filters)
2. EXPLORE FILTERS → (Optional: could go directly to Quick Recommend)
```

**Note:** Quick Recommend screen exists but isn't directly wired in current flow. To use it:
```typescript
// In App.tsx
<HomeScreen 
  onQuickRecommend={() => {
    setRecommendedMovies(MOVIES.sort((a, b) => b.rating - a.rating).slice(0, 8));
    setCurrentScreen('quick-recommend');
  }}
/>
```

---

## State Management

### App-Level State
```typescript
// Screen navigation
const [currentScreen, setCurrentScreen] = useState<AppScreen>('home');

// Modal state
const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

// Mood input state
const [moodInput, setMoodInput] = useState('');
const [isVoiceInput, setIsVoiceInput] = useState(false);

// Results state
const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([]);
```

### Component-Level State (Results Screen)
```typescript
// Card navigation
const [currentIndex, setCurrentIndex] = useState(0);

// User actions
const [savedMovies, setSavedMovies] = useState<Set<string>>(new Set());
const [likedMovies, setLikedMovies] = useState<string[]>([]);
const [dislikedMovies, setDislikedMovies] = useState<string[]>([]);
```

### Component-Level State (Explore Filters)
```typescript
const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
const [excludedGenres, setExcludedGenres] = useState<string[]>([]);
const [minRating, setMinRating] = useState([0.5]);
const [minPopularity, setMinPopularity] = useState([50]);
const [isPersonalized, setIsPersonalized] = useState(false);
```

---

## Data Flow Summary

### Movie Data Pipeline
```
Backend API
    ↓
adaptBackendMovies() (adapter)
    ↓
MOVIES array (App state)
    ↓
Filter/Sort Logic (Mood AI or Manual Filters)
    ↓
recommendedMovies array
    ↓
Results Screen (swipe cards)
    ↓
selectedMovie (for detail modal)
```

### User Interaction Pipeline
```
User Action (click/swipe/type)
    ↓
Event Handler (onMoodInput, onApplyFilters, etc.)
    ↓
State Update (setCurrentScreen, setRecommendedMovies)
    ↓
Component Re-render (AnimatePresence transitions)
    ↓
New Screen Display
```

---

## Animation & Transitions

### Screen Transitions
```typescript
<AnimatePresence mode="wait">
  {currentScreen === 'home' && <HomeScreen key="home" />}
  {currentScreen === 'mood-input' && <MoodInput key="mood-input" />}
  {currentScreen === 'results' && <ResultsScreen key="results" />}
</AnimatePresence>
```

**Effect:** 
- `mode="wait"` ensures old screen exits before new one enters
- Each screen has `key` prop for proper unmounting
- Smooth fade/slide transitions between screens

### Card Swipe Animation
```typescript
// Motion values for physics-based animation
const x = useMotionValue(0);
const rotate = useTransform(x, [-200, 200], [-15, 15]);
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0]);
```

### Modal Animation
```typescript
// Backdrop fade
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
/>

// Modal slide + fade
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: 20 }}
/>
```

---

## Back Navigation Map

```
Any Screen → Home (via onBack())
│
├── Mood Input → Home
├── Explore Filters → Home
├── Quick Recommend → Home
└── Results → Home

Movie Detail Modal → Previous Screen (via onClose())
```

**Note:** All screens have a back button that returns to Home, creating a hub-and-spoke navigation pattern.

---

## Error States & Edge Cases

### Empty Results
```typescript
// In Results Screen
if (movies.length === 0) {
  return (
    <div className="text-center">
      <p>No movies match your criteria</p>
      <button onClick={onBack}>Go back</button>
    </div>
  );
}
```

### End of Swipe Stack
```typescript
// In Results Screen
if (currentIndex >= movies.length) {
  return (
    <button onClick={() => setCurrentIndex(0)}>
      maybe this again
    </button>
  );
}
```

### AI No Match
```typescript
// In parseIntentAndRecommend()
return recommended.length > 0 
  ? recommended 
  : MOVIES.slice(0, 8); // Fallback to top 8
```

---

## Performance Considerations

### Screen Rendering
- Use `AnimatePresence` with `mode="wait"` to prevent multiple screens rendering
- Each screen has unique `key` prop for proper cleanup
- Modal overlay doesn't unmount main screen (overlay only)

### Card Stack Optimization
- Only render visible cards (current + 2 below)
- Use `z-index` stacking instead of rendering all cards
- Swipe physics use hardware-accelerated transforms

### Data Filtering
- Filter operations happen once on navigation
- Results cached in `recommendedMovies` state
- No re-filtering during swipes

---

## Future Enhancements

### Potential Flow Additions
1. **User Profile Screen** - Save preferences, viewing history
2. **Saved Movies Library** - View all bookmarked movies
3. **Recommendation History** - Review past mood inputs and results
4. **Onboarding Flow** - Initial preference setup
5. **Search Screen** - Direct movie title search

### State Persistence
```typescript
// Could add localStorage or backend sync
useEffect(() => {
  localStorage.setItem('savedMovies', JSON.stringify(savedMovies));
  localStorage.setItem('likedMovies', JSON.stringify(likedMovies));
}, [savedMovies, likedMovies]);
```

### Deep Linking
```typescript
// URL-based navigation
/home
/mood-input
/results?mood=lonely+at+3am
/movie/:id
```

---

## Summary

The OFF Hours app uses a **hub-and-spoke navigation** pattern where:
- **Home** is the central hub
- **3 entry points** lead to different discovery methods
- **Results** is the main interaction screen
- **Movie Detail** is an overlay modal accessible from multiple screens

The flow prioritizes **emotion-first discovery** through AI mood parsing while offering **manual control** via filters, maintaining the minimalist A24-inspired aesthetic throughout.
