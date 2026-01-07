import { motion } from 'motion/react';
import { Movie } from '../data/movies';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface CardStackSliderProps {
  movies: Movie[];
  onSelectMovie: (movie: Movie) => void;
}

export function CardStackSlider({ movies, onSelectMovie }: CardStackSliderProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
      {movies.map((movie, index) => (
        <motion.div
          key={movie.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ y: -8 }}
          className="group cursor-pointer"
          onClick={() => onSelectMovie(movie)}
        >
          <div className="relative bg-white border border-neutral-200 overflow-hidden shadow-lg hover:shadow-2xl transition-shadow duration-300">
            {/* Neon glow effect on hover */}
            <div className="absolute -inset-0.5 bg-gradient-to-br from-pink-500 via-purple-500 to-blue-500 opacity-0 group-hover:opacity-20 blur-sm transition-opacity duration-300 pointer-events-none" />
            
            {/* Image */}
            <div className="relative h-80 overflow-hidden bg-neutral-100">
              <motion.img
                src={movie.poster}
                alt={movie.title}
                className="w-full h-full object-cover"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.4 }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
              
              {/* Rating badge */}
              <div className="absolute top-4 right-4 px-3 py-1 bg-black/70 backdrop-blur-sm text-white text-sm">
                ★ {movie.rating.toFixed(1)}
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <h3 className="mb-2 text-neutral-900 line-clamp-2">
                {movie.title}
              </h3>
              
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs text-neutral-500">{movie.year}</span>
                <span className="text-xs text-neutral-400">•</span>
                <span className="text-xs text-neutral-500 uppercase tracking-wider">
                  {movie.genres[0]}
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {movie.mood.slice(0, 2).map((mood) => (
                  <span
                    key={mood}
                    className="px-2 py-1 text-xs text-neutral-600 border border-neutral-300 bg-neutral-50"
                  >
                    {mood}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
