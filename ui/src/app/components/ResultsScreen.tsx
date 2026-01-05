import { motion, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { ArrowLeft, Heart, X, Bookmark } from "lucide-react";
import { useState } from "react";
import type { MovieUI } from "@/app/types";

type ActionType = "like" | "dislike" | "save" | "skip";

interface ResultsScreenProps {
  movies: MovieUI[];
  moodInput: string;
  isVoice: boolean;
  onSelectMovie: (movie: MovieUI) => void;
  onBack: () => void;
  loading?: boolean;
  errorMsg?: string | null;

  // remonte les actions vers App pour sendFeedback()
  onAction?: (payload: {
    movieId: number;
    action: ActionType;
    context?: any;
  }) => void;
}

export function ResultsScreen({
  movies,
  moodInput,
  isVoice,
  onSelectMovie,
  onBack,
  loading = false,
  errorMsg = null,
  onAction,
}: ResultsScreenProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [likedMovies, setLikedMovies] = useState<Set<number>>(new Set());
  const [dislikedMovies, setDislikedMovies] = useState<Set<number>>(new Set());
  const [savedMovies, setSavedMovies] = useState<Set<number>>(new Set());

  const fireAction = (movieId: number, action: ActionType) => {
    onAction?.({
      movieId,
      action,
      context: {
        moodInput,
        isVoice,
        screen: "results",
        index: currentIndex,
      },
    });
  };

  const handleLike = (movieId: number) => {
    setLikedMovies((prev) => new Set([...prev, movieId]));
    setDislikedMovies((prev) => {
      const n = new Set(prev);
      n.delete(movieId);
      return n;
    });
    fireAction(movieId, "like");
  };

  const handleDislike = (movieId: number) => {
    setDislikedMovies((prev) => new Set([...prev, movieId]));
    setLikedMovies((prev) => {
      const n = new Set(prev);
      n.delete(movieId);
      return n;
    });
    fireAction(movieId, "dislike");
  };

  const handleSave = (movieId: number) => {
    setSavedMovies((prev) => {
      const n = new Set(prev);
      if (n.has(movieId)) n.delete(movieId);
      else n.add(movieId);
      return n;
    });
    fireAction(movieId, "save");
  };

  const handleSwipeComplete = (direction: "left" | "right" | "up" | "down", movieId: number) => {
    if (direction === "right") handleLike(movieId);
    else if (direction === "left") handleDislike(movieId);
    else fireAction(movieId, "skip");

    if (currentIndex < movies.length - 1) {
      setTimeout(() => setCurrentIndex(currentIndex + 1), 300);
    }
  };

  const handleMaybeThisAgain = () => {
    setCurrentIndex(0);
    setLikedMovies(new Set());
    setDislikedMovies(new Set());
    setSavedMovies(new Set());
  };

  const visibleMovies = movies.slice(currentIndex, currentIndex + 3);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 right-20 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-6 py-6 border-b border-neutral-800 relative z-10">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-neutral-400 hover:text-neutral-200 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">back</span>
          </button>

          <div className="text-center flex-1 px-4">
            <p className="text-xs text-neutral-500 mb-1 uppercase tracking-wider">
              {isVoice ? "voice recommendation" : "based on your mood"}
            </p>
            <p className="text-sm text-neutral-400 italic">"{moodInput}"</p>
          </div>

          <div className="w-20 text-right">
            <span className="text-xs text-neutral-500">
              {Math.min(currentIndex + 1, Math.max(movies.length, 1))}/{Math.max(movies.length, 1)}
            </span>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto"
        >
          {loading ? (
            <div className="text-center py-20">
              <h2 className="mb-4 text-neutral-50">finding something…</h2>
              <p className="text-neutral-500">fetching recommendations</p>
            </div>
          ) : errorMsg ? (
            <div className="text-center py-20">
              <h2 className="mb-4 text-neutral-50">something went wrong</h2>
              <p className="text-neutral-500">{errorMsg}</p>
              <button
                onClick={onBack}
                className="mt-8 px-8 py-4 bg-transparent border border-pink-500/30 hover:border-pink-500/60 text-neutral-50 transition-all backdrop-blur-sm hover:bg-pink-500/5"
              >
                go back
              </button>
            </div>
          ) : visibleMovies.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-20"
            >
              <h2 className="mb-4 text-neutral-50">that's all for now</h2>
              <p className="text-neutral-400 mb-8">you've seen all the recommendations</p>
              <button
                onClick={handleMaybeThisAgain}
                className="px-8 py-4 bg-transparent border border-pink-500/30 hover:border-pink-500/60 text-neutral-50 transition-all backdrop-blur-sm hover:bg-pink-500/5"
              >
                maybe this again
              </button>
            </motion.div>
          ) : (
            <div className="relative" style={{ height: "700px" }}>
              {visibleMovies.map((movie, index) => (
                <EditorialCard
                  key={movie.movieId}
                  movie={movie}
                  index={index}
                  isTop={index === 0}
                  isLiked={likedMovies.has(movie.movieId)}
                  isDisliked={dislikedMovies.has(movie.movieId)}
                  isSaved={savedMovies.has(movie.movieId)}
                  onLike={handleLike}
                  onDislike={handleDislike}
                  onSave={handleSave}
                  onSwipeComplete={handleSwipeComplete}
                  onSelectMovie={onSelectMovie}
                />
              ))}
            </div>
          )}
        </motion.div>

        {!loading && !errorMsg && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="max-w-2xl mx-auto mt-16 p-8 border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm"
          >
            <h3 className="text-sm mb-4 text-neutral-300">why these films?</h3>
            <p className="text-sm text-neutral-500 leading-relaxed mb-4">
              we select films based on your intent and constraints, then rank them with our recommendation system.
            </p>
            <p className="text-xs text-neutral-600">
              swipe right to like • swipe left to skip • tap save to bookmark
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}

interface EditorialCardProps {
  movie: MovieUI;
  index: number;
  isTop: boolean;
  isLiked: boolean;
  isDisliked: boolean;
  isSaved: boolean;
  onLike: (movieId: number) => void;
  onDislike: (movieId: number) => void;
  onSave: (movieId: number) => void;
  onSwipeComplete: (direction: "left" | "right" | "up" | "down", movieId: number) => void;
  onSelectMovie: (movie: MovieUI) => void;
}

function EditorialCard({
  movie,
  index,
  isTop,
  isLiked,
  isDisliked,
  isSaved,
  onLike,
  onDislike,
  onSave,
  onSwipeComplete,
  onSelectMovie,
}: EditorialCardProps) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-300, 300], [-15, 15]);
  const opacity = useTransform(x, [-300, -150, 0, 150, 300], [0, 1, 1, 1, 0]);

  const likeIndicatorOpacity = useTransform(x, [0, 100], [0, 1]);
  const dislikeIndicatorOpacity = useTransform(x, [-100, 0], [1, 0]);

  const handleDragEnd = (_: any, info: PanInfo) => {
    const threshold = 150;
    if (Math.abs(info.offset.x) > threshold) onSwipeComplete(info.offset.x > 0 ? "right" : "left", movie.movieId);
    else if (Math.abs(info.offset.y) > threshold) onSwipeComplete(info.offset.y > 0 ? "down" : "up", movie.movieId);
  };

  const yearLabel = movie.year ?? "";
  const genres = movie.genres ?? [];
  const rating = typeof movie.rating === "number" ? movie.rating : null;

  const posterSrc =
    movie.poster && movie.poster.length > 10
      ? movie.poster
      : "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1200";

  return (
    <motion.div
      className={`absolute inset-0 ${isTop ? "cursor-grab active:cursor-grabbing" : ""}`}
      style={{
        x: isTop ? x : 0,
        y: isTop ? y : 0,
        rotate: isTop ? rotate : 0,
        opacity: isTop ? opacity : 1,
        zIndex: 10 - index,
      }}
      initial={{ scale: 1 - index * 0.03, y: index * 12 }}
      animate={{ scale: 1 - index * 0.03, y: index * 12 }}
      drag={isTop ? true : false}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      onDragEnd={isTop ? handleDragEnd : undefined}
      whileTap={isTop ? { cursor: "grabbing" } : {}}
    >
      <motion.div className="bg-white border border-neutral-200 h-full overflow-hidden shadow-xl relative">
        <div className="relative h-2/3 overflow-hidden bg-neutral-100">
          <motion.img
            src={posterSrc}
            alt={movie.title}
            className="w-full h-full object-cover"
            whileHover={isTop ? { scale: 1.05 } : {}}
            transition={{ duration: 0.4 }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />

          {isTop && (
            <>
              <motion.div
                className="absolute top-8 left-8 px-6 py-3 bg-pink-500 text-white shadow-lg shadow-pink-500/50"
                style={{ opacity: likeIndicatorOpacity, rotate: 12 }}
              >
                <Heart className="w-8 h-8" />
              </motion.div>
              <motion.div
                className="absolute top-8 right-8 px-6 py-3 bg-blue-500 text-white shadow-lg shadow-blue-500/50"
                style={{ opacity: dislikeIndicatorOpacity, rotate: -12 }}
              >
                <X className="w-8 h-8" />
              </motion.div>
            </>
          )}

          <div className="absolute top-4 right-4 px-4 py-2 bg-black/60 backdrop-blur-sm text-white text-sm">
            {yearLabel}
          </div>
        </div>

        <div className="p-8 h-1/3 flex flex-col justify-between">
          <div>
            <h2
              className="mb-3 text-neutral-900 cursor-pointer hover:text-neutral-600 transition-colors"
              onClick={() => onSelectMovie(movie)}
            >
              {movie.title}
            </h2>

            <div className="flex flex-wrap gap-2 mb-4">
              {genres.slice(0, 3).map((genre) => (
                <span key={genre} className="px-3 py-1 text-xs uppercase tracking-wider text-neutral-500 border border-neutral-300">
                  {genre}
                </span>
              ))}
            </div>

            {movie.reason ? (
              <p className="text-sm text-neutral-600 leading-relaxed mb-6">
                <span className="italic">{movie.reason}</span>
              </p>
            ) : null}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDislike(movie.movieId);
              }}
              className={`p-3 border transition-all ${
                isDisliked
                  ? "border-blue-500 bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                  : "border-neutral-300 text-neutral-600 hover:border-blue-500 hover:text-blue-500"
              }`}
            >
              <X className="w-5 h-5" />
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike(movie.movieId);
              }}
              className={`p-3 border transition-all ${
                isLiked
                  ? "border-pink-500 bg-pink-500 text-white shadow-lg shadow-pink-500/30"
                  : "border-neutral-300 text-neutral-600 hover:border-pink-500 hover:text-pink-500"
              }`}
            >
              <Heart className="w-5 h-5" />
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onSave(movie.movieId);
              }}
              className={`p-3 border transition-all ${
                isSaved
                  ? "border-purple-500 bg-purple-500 text-white shadow-lg shadow-purple-500/30"
                  : "border-neutral-300 text-neutral-600 hover:border-purple-500 hover:text-purple-500"
              }`}
            >
              <Bookmark className="w-5 h-5" />
            </button>

            <div className="flex-1" />

            <div className="text-right">
              <div className="flex items-center gap-2">
                <span className="text-xs text-neutral-400">★</span>
                <span className="text-neutral-900">{rating !== null ? rating.toFixed(1) : "—"}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
