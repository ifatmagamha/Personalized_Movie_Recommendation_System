import { motion } from 'motion/react';
import { CardStackSlider } from './CardStackSlider';
import { Movie } from '../data/movies';
import { X } from 'lucide-react';

interface QuickRecommendProps {
  movies: Movie[];
  onSelectMovie: (movie: Movie) => void;
  onBack: () => void;
}

export function QuickRecommend({ movies, onSelectMovie, onBack }: QuickRecommendProps) {
  // For quick recommend, just show top rated films
  const topMovies = [...movies].sort((a, b) => b.rating - a.rating).slice(0, 8);

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900">
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <button
          onClick={onBack}
          className="w-10 h-10 flex items-center justify-center hover:bg-neutral-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 max-w-2xl mx-auto"
        >
          <h2 className="mb-4 text-neutral-900">
            Worth watching
          </h2>
          <p className="text-lg text-neutral-600">
            No questions asked. Just good films.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <CardStackSlider movies={topMovies} onSelectMovie={onSelectMovie} />
        </motion.div>

        {/* Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="max-w-xl mx-auto mt-16 text-center"
        >
          <p className="text-sm text-neutral-500">
            Curated selection of critically acclaimed and emotionally resonant films.
            No algorithm, no personalization, just quality.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
