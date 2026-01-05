import { motion, AnimatePresence } from 'motion/react';
import { X, Play, Plus, Star, Clock, Calendar, Users, Sparkles, Check } from 'lucide-react';
import { Movie } from '../data/movies';

interface MovieDetailModalProps {
  movie: Movie;
  isLiked: boolean;
  isInWatchlist: boolean;
  onClose: () => void;
  onToggleWatchlist: () => void;
}

export function MovieDetailModal({
  movie,
  isLiked,
  isInWatchlist,
  onClose,
  onToggleWatchlist,
}: MovieDetailModalProps) {
  // Generate AI explanation based on movie attributes
  const getAIExplanation = () => {
    const reasons = [];
    
    if (isLiked) {
      reasons.push("You loved similar movies in this genre");
    }
    
    if (movie.rating >= 8.5) {
      reasons.push("Highly rated by critics and audiences");
    }
    
    if (movie.year >= 2024) {
      reasons.push("Fresh new release");
    }
    
    reasons.push(`Features ${movie.tags[0]?.toLowerCase()} storytelling`);
    
    return reasons;
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 50 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 50 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900 to-purple-900 rounded-3xl shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 backdrop-blur rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Hero Image */}
          <div className="relative h-[400px] overflow-hidden">
            <img
              src={movie.poster}
              alt={movie.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent" />
          </div>

          {/* Content */}
          <div className="p-8 -mt-32 relative z-10">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-white mb-2">{movie.title}</h2>
                <div className="flex items-center gap-4 text-gray-300">
                  <div className="flex items-center gap-1">
                    <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    <span>{movie.rating}/10</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{movie.year}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{movie.duration} min</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mb-8">
              <button className="flex-1 px-6 py-3 bg-white text-black rounded-full flex items-center justify-center gap-2 hover:bg-gray-200 transition-colors">
                <Play className="w-5 h-5 fill-current" />
                Watch Now
              </button>
              <button
                onClick={onToggleWatchlist}
                className={`px-6 py-3 rounded-full flex items-center justify-center gap-2 transition-colors ${
                  isInWatchlist
                    ? 'bg-purple-600 hover:bg-purple-700'
                    : 'bg-white/20 hover:bg-white/30'
                }`}
              >
                {isInWatchlist ? <Check className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                {isInWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
              </button>
            </div>

            {/* AI Recommendation Explanation */}
            <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 mb-6 border border-purple-500/20">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="text-white">Why we recommend this</h3>
              </div>
              <ul className="space-y-2">
                {getAIExplanation().map((reason, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-2 text-gray-300"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2" />
                    <span>{reason}</span>
                  </motion.li>
                ))}
              </ul>
            </div>

            {/* Description */}
            <div className="mb-6">
              <h3 className="text-white mb-3">Synopsis</h3>
              <p className="text-gray-300 leading-relaxed">{movie.description}</p>
            </div>

            {/* Tags */}
            <div className="mb-6">
              <h3 className="text-white mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {movie.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-4 py-2 bg-white/10 rounded-full text-sm text-gray-300 border border-white/20"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Director & Cast */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-white mb-3">Director</h3>
                <p className="text-gray-300">{movie.director}</p>
              </div>
              <div>
                <h3 className="text-white mb-3">Cast</h3>
                <div className="flex items-center gap-2 text-gray-300">
                  <Users className="w-4 h-4" />
                  <p>{movie.cast.join(', ')}</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
