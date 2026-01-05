import { motion, AnimatePresence } from 'motion/react';
import { X, Calendar, Clock, User, ThumbsUp, ThumbsDown, Bookmark, BookmarkCheck } from 'lucide-react';
import { Movie } from '../data/movies';
import { useState } from 'react';

interface MovieDetailProps {
  movie: Movie;
  onClose: () => void;
  onFeedback?: (movieId: string, feedback: 'helpful' | 'not-helpful') => void;
}

export function MovieDetail({ movie, onClose, onFeedback }: MovieDetailProps) {
  const [saved, setSaved] = useState(false);
  const [feedback, setFeedback] = useState<'helpful' | 'not-helpful' | null>(null);

  const handleFeedback = (type: 'helpful' | 'not-helpful') => {
    setFeedback(type);
    onFeedback?.(movie.id, type);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      >
        <div className="absolute inset-0 overflow-y-auto">
          <div className="min-h-screen flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="relative w-full max-w-5xl bg-white shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-6 right-6 z-10 w-10 h-10 bg-white shadow-lg flex items-center justify-center hover:bg-neutral-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="grid md:grid-cols-2">
                {/* Left: Image */}
                <div className="relative h-[400px] md:h-auto">
                  <img
                    src={movie.poster}
                    alt={movie.title}
                    className="w-full h-full object-cover grayscale"
                  />
                  
                  {/* Subtle accent */}
                  <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-cyan-400/40 to-pink-400/40" />
                </div>

                {/* Right: Content */}
                <div className="p-8 md:p-12 flex flex-col">
                  <div className="flex-1">
                    <div className="mb-8">
                      <span className="text-xs text-neutral-500 uppercase tracking-wider mb-3 block">
                        {movie.genres.join(' • ')}
                      </span>
                      <h2 className="text-3xl mb-4 text-neutral-900">{movie.title}</h2>
                      
                      <div className="flex flex-wrap gap-4 text-sm text-neutral-600 mb-6">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          <span>{movie.year}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{movie.duration} min</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          <span>{movie.director}</span>
                        </div>
                      </div>

                      <p className="text-neutral-700 leading-relaxed mb-6">
                        {movie.description}
                      </p>

                      {/* Cinematography note */}
                      {movie.cinematography && (
                        <div className="mb-6 p-4 bg-neutral-50 border-l-2 border-neutral-300">
                          <p className="text-xs text-neutral-500 mb-1 uppercase tracking-wider">
                            Cinematography
                          </p>
                          <p className="text-sm text-neutral-600">
                            {movie.cinematography}
                          </p>
                        </div>
                      )}

                      {/* Cast */}
                      <div className="mb-6">
                        <p className="text-xs text-neutral-500 mb-2 uppercase tracking-wider">Cast</p>
                        <p className="text-sm text-neutral-700">
                          {movie.cast.join(', ')}
                        </p>
                      </div>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-2 mb-8">
                        {movie.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-3 py-1 text-xs border border-neutral-200 text-neutral-600"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 mb-6">
                      <button
                        onClick={() => setSaved(!saved)}
                        className={`flex-1 px-6 py-3 flex items-center justify-center gap-2 border transition-colors ${
                          saved
                            ? 'bg-neutral-900 text-white border-neutral-900'
                            : 'border-neutral-300 hover:border-neutral-900'
                        }`}
                      >
                        {saved ? (
                          <>
                            <BookmarkCheck className="w-4 h-4" />
                            <span className="text-sm">Saved</span>
                          </>
                        ) : (
                          <>
                            <Bookmark className="w-4 h-4" />
                            <span className="text-sm">Save</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Feedback */}
                    <div className="pt-6 border-t border-neutral-200">
                      <p className="text-xs text-neutral-500 mb-3 uppercase tracking-wider">
                        Was this recommendation helpful?
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleFeedback('helpful')}
                          className={`flex-1 px-4 py-2 flex items-center justify-center gap-2 border transition-colors ${
                            feedback === 'helpful'
                              ? 'bg-neutral-900 text-white border-neutral-900'
                              : 'border-neutral-300 hover:border-neutral-900'
                          }`}
                        >
                          <ThumbsUp className="w-4 h-4" />
                          <span className="text-sm">Yes</span>
                        </button>
                        <button
                          onClick={() => handleFeedback('not-helpful')}
                          className={`flex-1 px-4 py-2 flex items-center justify-center gap-2 border transition-colors ${
                            feedback === 'not-helpful'
                              ? 'bg-neutral-900 text-white border-neutral-900'
                              : 'border-neutral-300 hover:border-neutral-900'
                          }`}
                        >
                          <ThumbsDown className="w-4 h-4" />
                          <span className="text-sm">No</span>
                        </button>
                      </div>
                      {feedback && (
                        <motion.p
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="text-xs text-neutral-500 mt-2"
                        >
                          Thanks for your feedback
                        </motion.p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
