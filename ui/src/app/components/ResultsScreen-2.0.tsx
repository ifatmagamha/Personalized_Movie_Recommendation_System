import { motion, useMotionValue, useTransform, PanInfo } from 'motion/react';
import { ArrowLeft, Heart, X, Bookmark } from 'lucide-react';
import { Movie } from '../data/movies';
import { useState } from 'react';

interface ResultsScreenProps {
  movies: Movie[];
  moodInput: string;
  isVoice: boolean;
  onSelectMovie: (movie: Movie) => void;
  onBack: () => void;
}

export function ResultsScreen({ movies, moodInput, isVoice, onSelectMovie, onBack }: ResultsScreenProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [likedMovies, setLikedMovies] = useState<Set<string>>(new Set());
  const [dislikedMovies, setDislikedMovies] = useState<Set<string>>(new Set());
  const [savedMovies, setSavedMovies] = useState<Set<string>>(new Set());

  const handleLike = (movieId: string) => {
    setLikedMovies(prev => new Set([...prev, movieId]));
    setDislikedMovies(prev => {
      const newSet = new Set(prev);
      newSet.delete(movieId);
      return newSet;
    });
  };

  const handleDislike = (movieId: string) => {
    setDislikedMovies(prev => new Set([...prev, movieId]));
    setLikedMovies(prev => {
      const newSet = new Set(prev);
      newSet.delete(movieId);
      return newSet;
    });
  };

  const handleSave = (movieId: string) => {
    setSavedMovies(prev => {
      const newSet = new Set(prev);
      if (newSet.has(movieId)) {
        newSet.delete(movieId);
      } else {
        newSet.add(movieId);
      }
      return newSet;
    });
  };

  const handleSwipeComplete = (direction: 'left' | 'right' | 'up' | 'down', movieId: string) => {
    // Handle feedback based on swipe direction
    if (direction === 'right') {
      handleLike(movieId);
      console.log(`Liked: ${movieId}`);
    } else if (direction === 'left') {
      handleDislike(movieId);
      console.log(`Disliked: ${movieId}`);
    }
    
    if (currentIndex < movies.length - 1) {
      setTimeout(() => {
        setCurrentIndex(currentIndex + 1);
      }, 300);
    }
  };

  const handleMaybeThisAgain = () => {
    // Reset to beginning or could call recommend API again
    setCurrentIndex(0);
    setLikedMovies(new Set());
    setDislikedMovies(new Set());
    setSavedMovies(new Set());
  };

  const visibleMovies = movies.slice(currentIndex, currentIndex + 3);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden">
      {/* Neon accent background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 right-20 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
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
              {isVoice ? 'voice recommendation' : 'based on your mood'}
            </p>
            <p className="text-sm text-neutral-400 italic">"{moodInput}"</p>
          </div>

          <div className="w-20 text-right">
            <span className="text-xs text-neutral-500">
              {currentIndex + 1}/{movies.length}
            </span>
          </div>
        </div>
      </div>

      {/* Card Stack */}
      <div className="container mx-auto px-4 py-12 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto"
        >
          {visibleMovies.length === 0 ? (
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
            <div className="relative" style={{ height: '700px' }}>
              {visibleMovies.map((movie, index) => (
                <EditorialCard
                  key={movie.id}
                  movie={movie}
                  index={index}
                  isTop={index === 0}
                  isLiked={likedMovies.has(movie.id)}
                  isDisliked={dislikedMovies.has(movie.id)}
                  isSaved={savedMovies.has(movie.id)}
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

        {/* Explanation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="max-w-2xl mx-auto mt-16 p-8 border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm"
        >
          <h3 className="text-sm mb-4 text-neutral-300">why these films?</h3>
          <p className="text-sm text-neutral-500 leading-relaxed mb-4">
            our intent parser analyzed the emotional context of your input. rather than matching keywords, 
            we identified the underlying mood and energy you're seeking.
          </p>
          <p className="text-xs text-neutral-600">
            swipe right to like • swipe left to skip • tap save to bookmark
          </p>
        </motion.div>
      </div>
    </div>
  );
}

interface EditorialCardProps {
  movie: Movie;
  index: number;
  isTop: boolean;
  isLiked: boolean;
  isDisliked: boolean;
  isSaved: boolean;
  onLike: (id: string) => void;
  onDislike: (id: string) => void;
  onSave: (id: string) => void;
  onSwipeComplete: (direction: 'left' | 'right' | 'up' | 'down', movieId: string) => void;
  onSelectMovie: (movie: Movie) => void;
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
  const opacity = useTransform(
    x,
    [-300, -150, 0, 150, 300],
    [0, 1, 1, 1, 0]
  );

  // Swipe indicator opacities - always define hooks at top level
  const likeIndicatorOpacity = useTransform(x, [0, 100], [0, 1]);
  const dislikeIndicatorOpacity = useTransform(x, [-100, 0], [1, 0]);

  const handleDragEnd = (_: any, info: PanInfo) => {
    const threshold = 150;
    
    if (Math.abs(info.offset.x) > threshold) {
      onSwipeComplete(info.offset.x > 0 ? 'right' : 'left', movie.id);
    } else if (Math.abs(info.offset.y) > threshold) {
      onSwipeComplete(info.offset.y > 0 ? 'down' : 'up', movie.id);
    }
  };

  const reasonText = movie.mood.slice(0, 2).join(', ');

  return (
    <motion.div
      className={`absolute inset-0 ${isTop ? 'cursor-grab active:cursor-grabbing' : ''}`}
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
      whileTap={isTop ? { cursor: 'grabbing' } : {}}
    >
      <motion.div
        className="bg-white border border-neutral-200 h-full overflow-hidden shadow-xl relative"
        whileHover={isTop ? { boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)' } : {}}
      >
        {/* Neon glow on hover */}
        {isTop && (
          <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-20 blur transition-opacity pointer-events-none" />
        )}

        {/* Image */}
        <div className="relative h-2/3 overflow-hidden bg-neutral-100">
          <motion.img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover"
            whileHover={isTop ? { scale: 1.05 } : {}}
            transition={{ duration: 0.4 }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
          
          {/* Swipe indicators */}
          {isTop && (
            <>
              <motion.div
                className="absolute top-8 left-8 px-6 py-3 bg-pink-500 text-white shadow-lg shadow-pink-500/50"
                style={{ 
                  opacity: likeIndicatorOpacity,
                  rotate: 12 
                }}
              >
                <Heart className="w-8 h-8" />
              </motion.div>
              <motion.div
                className="absolute top-8 right-8 px-6 py-3 bg-blue-500 text-white shadow-lg shadow-blue-500/50"
                style={{ 
                  opacity: dislikeIndicatorOpacity,
                  rotate: -12 
                }}
              >
                <X className="w-8 h-8" />
              </motion.div>
            </>
          )}

          {/* Year badge */}
          <div className="absolute top-4 right-4 px-4 py-2 bg-black/60 backdrop-blur-sm text-white text-sm">
            {movie.year}
          </div>
        </div>

        {/* Content */}
        <div className="p-8 h-1/3 flex flex-col justify-between">
          <div>
            <h2 
              className="mb-3 text-neutral-900 cursor-pointer hover:text-neutral-600 transition-colors"
              onClick={() => onSelectMovie(movie)}
            >
              {movie.title}
            </h2>
            
            {/* Genres */}
            <div className="flex flex-wrap gap-2 mb-4">
              {movie.genres.slice(0, 3).map((genre) => (
                <span
                  key={genre}
                  className="px-3 py-1 text-xs uppercase tracking-wider text-neutral-500 border border-neutral-300"
                >
                  {genre}
                </span>
              ))}
            </div>

            {/* Reason text */}
            <p className="text-sm text-neutral-600 leading-relaxed mb-6">
              For when you're feeling <span className="italic">{reasonText}</span>
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDislike(movie.id);
              }}
              className={`
                p-3 border transition-all
                ${isDisliked
                  ? 'border-blue-500 bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                  : 'border-neutral-300 text-neutral-600 hover:border-blue-500 hover:text-blue-500'
                }
              `}
            >
              <X className="w-5 h-5" />
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onLike(movie.id);
              }}
              className={`
                p-3 border transition-all
                ${isLiked
                  ? 'border-pink-500 bg-pink-500 text-white shadow-lg shadow-pink-500/30'
                  : 'border-neutral-300 text-neutral-600 hover:border-pink-500 hover:text-pink-500'
                }
              `}
            >
              <Heart className="w-5 h-5" />
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onSave(movie.id);
              }}
              className={`
                p-3 border transition-all
                ${isSaved
                  ? 'border-purple-500 bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                  : 'border-neutral-300 text-neutral-600 hover:border-purple-500 hover:text-purple-500'
                }
              `}
            >
              <Bookmark className="w-5 h-5" />
            </button>

            <div className="flex-1" />

            <div className="text-right">
              <div className="flex items-center gap-2">
                <span className="text-xs text-neutral-400">★</span>
                <span className="text-neutral-900">{movie.rating.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
