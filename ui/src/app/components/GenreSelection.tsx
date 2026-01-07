import { useState } from 'react';
import { motion } from 'motion/react';
import { GENRES } from '../data/movies';
import { ArrowRight } from 'lucide-react';

interface GenreSelectionProps {
  onComplete: (selectedGenres: string[]) => void;
}

export function GenreSelection({ onComplete }: GenreSelectionProps) {
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);

  const toggleGenre = (genreId: string) => {
    setSelectedGenres((prev) =>
      prev.includes(genreId)
        ? prev.filter((id) => id !== genreId)
        : [...prev, genreId]
    );
  };

  const handleContinue = () => {
    if (selectedGenres.length > 0) {
      onComplete(selectedGenres);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white px-4 py-16">
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="mb-4">What do you love to watch?</h1>
          <p className="text-xl text-gray-300">
            Select at least one genre to get started
          </p>
          <p className="text-sm text-gray-400 mt-2">
            {selectedGenres.length} genre{selectedGenres.length !== 1 ? 's' : ''} selected
          </p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-12">
          {GENRES.map((genre, index) => {
            const isSelected = selectedGenres.includes(genre.id);
            return (
              <motion.button
                key={genre.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => toggleGenre(genre.id)}
                className={`relative overflow-hidden rounded-2xl p-6 aspect-square flex flex-col items-center justify-center gap-3 border-2 transition-all ${
                  isSelected
                    ? 'border-white shadow-lg shadow-purple-500/50'
                    : 'border-white/20 hover:border-white/40'
                }`}
              >
                {/* Gradient background */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${genre.color} opacity-${
                    isSelected ? '100' : '60'
                  } transition-opacity`}
                />

                {/* Content */}
                <div className="relative z-10">
                  <div className="text-5xl mb-2">{genre.icon}</div>
                  <div className="text-sm">{genre.name}</div>
                </div>

                {/* Selection indicator */}
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-2 right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center"
                  >
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                  </motion.div>
                )}
              </motion.button>
            );
          })}
        </div>

        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <button
            onClick={handleContinue}
            disabled={selectedGenres.length === 0}
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full text-lg transition-all ${
              selectedGenres.length > 0
                ? 'bg-gradient-to-r from-pink-500 to-purple-600 hover:shadow-lg hover:shadow-purple-500/50 hover:scale-105'
                : 'bg-gray-600 opacity-50 cursor-not-allowed'
            }`}
          >
            Continue
            <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
