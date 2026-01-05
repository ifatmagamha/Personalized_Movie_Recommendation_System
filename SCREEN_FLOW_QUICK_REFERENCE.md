# Screen Flow - Quick Reference

## 🗺️ Visual Navigation Map

```
                    ┌─────────────────────┐
                    │   1. HOME SCREEN    │
                    │  "(Maybe THIS.)"    │
                    │                     │
                    │ ┌─────────────────┐ │
                    │ │ Tell us how     │ │
                    │ │ you're feeling  │ │
                    │ └─────────────────┘ │
                    │ ┌─────────────────┐ │
                    │ │ I just need     │ │
                    │ │ something       │ │
                    │ └─────────────────┘ │
                    └──────┬──────┬───────┘
                           │      │
              ┌────────────┘      └────────────┐
              │                                │
              ▼                                ▼
┌──────────────────────┐          ┌──────────────────────┐
│  2. MOOD INPUT       │          │  3. EXPLORE FILTERS  │
│                      │          │                      │
│  ┌────────────────┐  │          │  [Popular/Personal]  │
│  │ Type mood...   │  │          │                      │
│  │ "lonely 3am"   │  │          │  ✓ Drama    + -      │
│  └────────────────┘  │          │  ✓ Romance  + -      │
│  🎤 Voice Input      │          │  ✗ Horror   + -      │
│                      │          │                      │
│  [Submit]            │          │  Rating:  ⚫─────○   │
│                      │          │                      │
└──────────┬───────────┘          │  [Show Results]      │
           │                      └──────────┬───────────┘
           │  AI Mood Parser               │
           │  Detects emotions             │  Manual Filters
           │  Scores movies                │  Include/Exclude
           │                               │
           └───────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │   5. RESULTS        │
              │   Swipe Cards       │
              │                     │
              │   ┌─────────────┐   │
              │   │   Movie 1   │   │ ← Top card (swipeable)
              │   │  [Poster]   │   │
              │   │   Title     │   │
              │   └─────────────┘   │
              │    ┌───────────┐    │ ← Card 2
              │     ┌─────────┐     │ ← Card 3
              │                     │
              │   ✗    💾    ❤️     │
              │ Dislike Save Like   │
              │                     │
              └──────────┬──────────┘
                         │
                         │ Click card
                         ▼
              ┌─────────────────────┐
              │  MOVIE DETAIL       │
              │  (Modal Overlay)    │
              │                     │
              │  [Poster] Synopsis  │
              │           Year      │
              │           Duration  │
              │           Cast      │
              │           Rating    │
              │                     │
              │  [Save] [Like] [×]  │
              └─────────────────────┘
```

---

## 🎯 Entry Points from Home

| Button | Action | Leads To | Purpose |
|--------|--------|----------|---------|
| **"tell us how you're feeling"** | Emotion input | Mood Input → Results | AI-powered recommendations |
| **"i just need something"** | Quick browse | Explore Filters → Results | Manual filter selection |

---

## 📊 Screen Data Requirements

### Home Screen
```typescript
Props: None
State: None
Data: None
```

### Mood Input Screen
```typescript
Props:
  - onSubmit(input: string, isVoice: boolean)
  - onBack()

Internal State:
  - input: string (user's typed text)
  - isRecording: boolean (voice input active)

Output Data:
  → moodInput: "lonely at 3am"
  → isVoiceInput: true/false
  → recommendedMovies: Movie[] (AI-filtered, top 10)
```

### Explore Filters Screen
```typescript
Props:
  - onApplyFilters(filters: FilterState)
  - onBack()

Internal State:
  - selectedGenres: string[]
  - excludedGenres: string[]
  - minRating: number
  - isPersonalized: boolean

Output Data:
  → moodInput: "Filtered results"
  → recommendedMovies: Movie[] (filtered, up to 12)
```

### Results Screen
```typescript
Props:
  - movies: Movie[] (incoming recommendations)
  - moodInput: string (original mood/filter label)
  - isVoice: boolean
  - onSelectMovie(movie: Movie)
  - onBack()

Internal State:
  - currentIndex: number (which card)
  - savedMovies: Set<string>
  - likedMovies: string[]
  - dislikedMovies: string[]

Output Data:
  → selectedMovie: Movie (for detail modal)
```

### Movie Detail Modal
```typescript
Props:
  - movie: Movie (selected movie)
  - onClose()
  - onFeedback(movieId: string, type: 'helpful' | 'not-helpful')

Internal State:
  - saved: boolean

Output Data:
  → Feedback data (for backend)
```

---

## 🔄 State Flow Diagram

```
                    ┌──────────────────┐
                    │   APP STATE      │
                    │                  │
                    │ currentScreen    │──┐
                    │ selectedMovie    │  │
                    │ moodInput        │  │ Controls what
                    │ recommendedMovies│  │ screen renders
                    └──────────────────┘  │
                              │           │
              ┌───────────────┴───────────┴──────────┐
              │                                      │
              ▼                                      ▼
    USER INTERACTION                        COMPONENT RENDER
    (clicks, swipes, types)                 (based on state)
              │                                      │
              │                                      │
              ▼                                      │
    EVENT HANDLER                                    │
    (onMoodInput, onApplyFilters, etc.)             │
              │                                      │
              │                                      │
              ▼                                      │
    STATE UPDATE                                     │
    (setCurrentScreen, setMovies, etc.)             │
              │                                      │
              └──────────────────────────────────────┘
```

---

## ⚡ Key User Flows

### Flow A: "I'm lonely at 3am"
```
1. HOME
   ↓ Click "tell us how you're feeling"
2. MOOD INPUT
   ↓ Type "lonely at 3am vibes" + Submit
   → AI detects moods: [lonely, melancholic, contemplative]
   → Scores all movies for mood match
   → Returns top 10: mostly Drama/Romance with quiet moods
3. RESULTS
   ↓ Browse 10 swipe cards
   ↓ Swipe right on "Eternal Echoes" (melancholic romance)
   ↓ Click card to see details
4. MOVIE DETAIL
   ↓ Read synopsis, see it's 108min, contemplative mood
   ↓ Click Save
   ↓ Close modal
   ↓ Continue swiping through recommendations
```

### Flow B: "I want thriller but not horror"
```
1. HOME
   ↓ Click "i just need something"
2. EXPLORE FILTERS
   ↓ Click Thriller (+)
   ↓ Click Horror (-)
   ↓ Set minimum rating to 7.5
   ↓ Toggle to "Popular"
   ↓ Click "Show Results"
   → Filters to Drama/Thriller, excludes Horror
   → Sorts by rating descending
   → Returns top 12 matches
3. RESULTS
   ↓ Browse filtered swipe cards
   ↓ All cards are Thriller without Horror elements
```

### Flow C: "Just show me something good"
```
1. HOME
   ↓ Click "i just need something"
2. EXPLORE FILTERS
   ↓ Don't select any genres (all allowed)
   ↓ Set minimum rating to 8.5
   ↓ Toggle to "Popular"
   ↓ Click "Show Results"
   → Returns highest-rated movies only
3. RESULTS
   ↓ See only movies rated 8.5+
```

---

## 🎬 Swipe Card Mechanics

### Card Stack Display
```
┌─────────────────┐ ← Card 1 (z-index: 30, fully interactive)
│     MOVIE 1     │   
│                 │   
│   [Poster]      │   Swipe Right → Like (pink heart)
│                 │   Swipe Left  → Dislike (blue X)
│   Title         │   Click       → Detail Modal
│   ★ 8.7         │
└─────────────────┘
 ┌───────────────┐  ← Card 2 (z-index: 20, static, scaled 95%)
  ┌─────────────┐   ← Card 3 (z-index: 10, static, scaled 90%)
```

### Swipe Thresholds
- **Drag distance:** 100px horizontal triggers auto-complete
- **Visual feedback:** 
  - Heart opacity: 0 → 1 as drag right
  - X opacity: 0 → 1 as drag left
  - Card rotation: -15° to +15° based on drag
- **Physics:** Spring animation on release

### Button Actions
| Button | Icon | Color | Action |
|--------|------|-------|--------|
| Dislike | ✗ | Blue | Same as swipe left |
| Save | 💾 | White | Bookmark (stays in stack) |
| Like | ❤️ | Pink | Same as swipe right |

---

## 🧠 AI Mood Parser Logic

### Pattern Detection
```typescript
Input: "feeling lonely at 3am can't sleep"

Detected Patterns:
  ✓ "lonely" → [lonely, melancholic, contemplative]
  ✓ "3am" → [contemplative, calm]
  ✓ "can't sleep" → [contemplative, calm, peaceful]

Combined Moods: [lonely, melancholic, contemplative, calm, peaceful]

Scoring Movies:
  "Eternal Echoes" (Drama/Romance)
    - mood: [melancholic, romantic, lonely, peaceful]
    - Match: lonely(+3), melancholic(+3), peaceful(+3) = 9 points
    - Genre: Drama matches melancholic mood (+2)
    - Rating: 8.7 (+1 bonus)
    - TOTAL: 12 points ⭐

  "Drive Nowhere" (Thriller)
    - mood: [tense, cool, focused, anxious]
    - Match: 0 points (no mood overlap)
    - TOTAL: 0 points (filtered out)

Results: Top 10 highest scoring movies
```

### Intent Pattern Examples
| Input | Detected Intent | Mapped Moods |
|-------|----------------|--------------|
| "broke up with someone" | Heartbreak | sad, melancholic, reflective |
| "need a laugh" | Comedy request | happy, light, playful |
| "can't sleep" | Insomnia | contemplative, calm, peaceful |
| "feeling weird tonight" | Experimental | curious, contemplative |
| "3am vibes" | Late night | contemplative, melancholic |
| "stressed from work" | Anxiety relief | peaceful, calm, relaxed |

---

## 🔙 Back Navigation Rules

All screens follow this pattern:
```typescript
// Top-left corner always has back button
<button onClick={onBack} className="...">
  <ArrowLeft /> Back
</button>

// All onBack handlers return to home
onBack={() => setCurrentScreen('home')}
```

**Exception:** Movie Detail Modal
- Close button (X) in top-right
- Closes modal, returns to previous screen
- Backdrop click also closes

---

## 💾 Data Persistence Points

### Currently Session-Only
- Liked movies
- Disliked movies
- Saved movies
- Current swipe position
- Filter selections

### Could Persist (with Backend)
```typescript
// After each action
await fetch('/api/user/actions', {
  method: 'POST',
  body: JSON.stringify({
    movieId: movie.id,
    action: 'like' | 'dislike' | 'save',
    timestamp: Date.now(),
    context: moodInput, // What led to this movie
  })
});

// Load on app init
const savedData = await fetch('/api/user/saved-movies');
setSavedMovies(new Set(savedData.movieIds));
```

---

## 🎨 Visual Feedback Summary

### Screen Transitions
- **Type:** Fade + slide
- **Duration:** 0.3s
- **Easing:** Ease-in-out

### Card Swipes
- **Type:** Physics-based drag
- **Spring:** Stiffness 300, damping 30
- **Indicators:** Fade in during drag

### Button Hovers
- **Border:** Glow effect (neon accent)
- **Background:** Subtle color wash
- **Duration:** 0.2s

### Modal
- **Backdrop:** Fade to black/60
- **Content:** Slide up + fade
- **Duration:** 0.4s

---

## 📱 Responsive Considerations

### Mobile (< 768px)
- Single column layouts
- Full-screen swipe cards
- Bottom sheet for filters
- Larger touch targets

### Desktop (≥ 768px)
- Centered content (max-width)
- Two-column Movie Detail
- Hover states active
- Keyboard shortcuts possible

---

## ⚠️ Edge Cases Handled

| Situation | Behavior |
|-----------|----------|
| No movies match filter | Show empty state, button to go back |
| AI finds no mood match | Return top 8 rated movies as fallback |
| User swipes through all cards | Show "maybe this again" button to restart |
| Empty mood input | Prevent submit or use default moods |
| Network error on voice input | Fall back to text input |

---

## 🚀 Quick Integration Checklist

- [ ] Connect Home screen navigation handlers
- [ ] Wire up Mood Input AI parser to backend (or use client-side)
- [ ] Connect Explore Filters to movie filtering logic
- [ ] Set up Results screen with swipe handlers
- [ ] Configure Movie Detail modal with save/feedback API
- [ ] Add AnimatePresence wrapper for smooth transitions
- [ ] Test all back navigation paths return to Home
- [ ] Verify modal opens/closes correctly from any screen

---

## 🎯 Summary

**5 Main Screens:**
1. Home (hub)
2. Mood Input (AI entry)
3. Explore Filters (manual entry)
4. Results (swipe interface)
5. Movie Detail (modal overlay)

**2 Recommendation Paths:**
- Emotion-first (AI mood parsing)
- Control-first (manual filters)

**1 Interaction Model:**
- Hub-and-spoke navigation
- All roads lead back to Home
- Modal overlay for details

**Core Flow:**
`Home → (Mood OR Filters) → Results → Detail → Repeat`
