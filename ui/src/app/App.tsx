import { useState } from "react";
import { AnimatePresence } from "framer-motion";

import { HomeScreen } from "./components/HomeScreen";
import { MoodInput } from "./components/MoodInput";
import { ExploreFilters, FilterState } from "./components/ExploreFilters";
import { ResultsScreen } from "./components/ResultsScreen";
import { MovieDetail } from "./components/MovieDetail";

import { recommend, sendFeedback } from "@/lib/api";
import { mapMovieRecToUI } from "@/lib/mappers";
import type { MovieUI } from "@/app/types";

type AppScreen = "home" | "mood-input" | "explore-filters" | "results";

type ActionType = "like" | "dislike" | "save" | "skip" | "helpful" | "not_helpful";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>("home");
  const [selectedMovie, setSelectedMovie] = useState<MovieUI | null>(null);

  const [moodInput, setMoodInput] = useState("");
  const [isVoiceInput, setIsVoiceInput] = useState(false);

  const [recommendedMovies, setRecommendedMovies] = useState<MovieUI[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [swipedMovieIds, setSwipedMovieIds] = useState<Set<number>>(new Set());
  const [likedMovieIds, setLikedMovieIds] = useState<Set<number>>(new Set());

  const userId = null; // future: brancher user profile

  const handleBack = () => {
    setCurrentScreen("home");
    setSelectedMovie(null);
    setErrorMsg(null);
  };

  const handleMovieSelect = (movie: MovieUI) => setSelectedMovie(movie);

  const handleMoodSubmit = async (input: string, isVoice: boolean) => {
    setMoodInput(input);
    setIsVoiceInput(isVoice);
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await recommend({
        user_id: userId,
        query: input,
        k: 12,
        mode: "auto",
        candidate_pool: 2000,
      });

      const uiMovies = (res.recommendations ?? []).map(mapMovieRecToUI);
      setRecommendedMovies(uiMovies);
      setCurrentScreen("results");
    } catch (e: any) {
      setErrorMsg(e?.message ?? "Failed to fetch recommendations");
      setRecommendedMovies([]);
      setCurrentScreen("results");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = async (filters: FilterState) => {
    setMoodInput("Filtered results");
    setIsVoiceInput(false);
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await recommend({
        user_id: userId,
        k: 48,
        mode: filters.isPersonalized ? "cf" : "baseline",
        candidate_pool: 5000,
        constraints: {
          genres_in: filters.selectedGenres.length ? filters.selectedGenres : undefined,
          genres_out: filters.excludedGenres.length ? filters.excludedGenres : undefined,
          min_avg_rating: filters.minRating > 0 ? filters.minRating : undefined,
          min_n_ratings: filters.minPopularity > 0 ? Math.floor(filters.minPopularity) : undefined,
        },
      });

      const uiMovies = (res.recommendations ?? []).map(mapMovieRecToUI);
      setRecommendedMovies(uiMovies);
      setCurrentScreen("results");
    } catch (e: any) {
      setErrorMsg(e?.message ?? "Failed to fetch recommendations");
      setRecommendedMovies([]);
      setCurrentScreen("results");
    } finally {
      setLoading(false);
    }
  };

  // Unified feedback sender (best effort)
  const postFeedback = async (payload: { movieId: number; action: ActionType; context?: any }) => {
    try {
      await sendFeedback({
        user_id: userId,
        movieId: payload.movieId,
        action: payload.action as any,
        context: {
          moodInput,
          isVoice: isVoiceInput,
          screen: currentScreen,
          ...(payload.context ?? {}),
        },
      });
    } catch {
      // best effort (ne casse pas l'UX)
    }
  };

  // Helper: extract genres from liked movies for refinement
  const extractGenresFromLiked = (likedIds: Set<number>): string[] => {
    const likedMovies = recommendedMovies.filter(m => likedIds.has(m.movieId));
    const genreSet = new Set<string>();
    likedMovies.forEach(m => {
      (m.genres ?? []).forEach(g => genreSet.add(g));
    });
    return Array.from(genreSet);
  };

  // Refine recommendations based on swipe feedback
  const refineRecommendations = async () => {
    if (loading) return; // Prevent concurrent requests
    
    setLoading(true);
    setErrorMsg(null);

    try {
      const likedGenres = extractGenresFromLiked(likedMovieIds);
      
      const res = await recommend({
        user_id: userId,
        k: 12,
        mode: "auto",
        candidate_pool: 2000,
        constraints: {
          exclude_movieIds: Array.from(swipedMovieIds), // Exclude already swiped
          genres_in: likedGenres.length > 0 ? likedGenres : undefined, // Prefer genres from liked movies
        },
      });

      const newMovies = (res.recommendations ?? []).map(mapMovieRecToUI);
      
      // Append new movies, avoiding duplicates
      setRecommendedMovies(prev => {
        const existingIds = new Set(prev.map(m => m.movieId));
        const unique = newMovies.filter(m => !existingIds.has(m.movieId));
        return [...prev, ...unique];
      });
    } catch (e: any) {
      setErrorMsg(e?.message ?? "Failed to refine recommendations");
    } finally {
      setLoading(false);
    }
  };

  // Handle swipe action with automatic refinement
  const handleSwipeAction = async (
    movieId: number,
    action: "like" | "dislike" | "skip",
    shouldRefine: boolean = false
  ) => {
    // Track swiped movies
    setSwipedMovieIds(prev => new Set([...prev, movieId]));
    
    if (action === "like") {
      setLikedMovieIds(prev => new Set([...prev, movieId]));
    }

    // Send feedback
    await postFeedback({
      movieId,
      action,
      context: { source: "swipe", screen: "results" },
    });

    // If near end of recommendations and should refine, fetch more
    if (shouldRefine && currentScreen === "results") {
      const remaining = recommendedMovies.length - swipedMovieIds.size - 1; // -1 for current swipe
      if (remaining <= 3) {
        await refineRecommendations();
      }
    }
  };

  // From MovieDetail: helpful / not-helpful (string id from UI)
  const handleFeedback = async (movieId: string, feedback: "helpful" | "not-helpful") => {
    const mid = Number(movieId);
    if (Number.isNaN(mid)) return;

    await postFeedback({
      movieId: mid,
      action: feedback === "helpful" ? "helpful" : "not_helpful",
      context: { source: "detail" },
    });
  };

  return (
    <div className="min-h-screen bg-neutral-950">
      <AnimatePresence mode="wait">
        {currentScreen === "home" && (
          <HomeScreen
            key="home"
            onQuickRecommend={() => setCurrentScreen("explore-filters")}
            onMoodInput={() => setCurrentScreen("mood-input")}
          />
        )}

        {currentScreen === "mood-input" && (
          <MoodInput key="mood-input" onSubmit={handleMoodSubmit} onBack={handleBack} />
        )}

        {currentScreen === "explore-filters" && (
          <ExploreFilters key="explore-filters" onApplyFilters={handleApplyFilters} onBack={handleBack} />
        )}

        {currentScreen === "results" && (
          <ResultsScreen
            key="results"
            movies={recommendedMovies}
            moodInput={loading ? "loading…" : moodInput}
            isVoice={isVoiceInput}
            onSelectMovie={handleMovieSelect}
            onBack={handleBack}
            errorMsg={errorMsg}
            loading={loading}
            onAction={({ movieId, action, context }) => {
              const shouldRefine = context?.shouldRefine ?? false;
              handleSwipeAction(movieId, action as "like" | "dislike" | "skip", shouldRefine);
            }}
          />
        )}
      </AnimatePresence>

      {selectedMovie && (
        <MovieDetail
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onFeedback={handleFeedback}
          onAction={({ movieId, action, context }) =>
            postFeedback({ movieId, action, context: { source: "detail", ...(context ?? {}) } })
          }
        />
      )}
    </div>
  );
}