import { motion } from 'motion/react';
import { X, User, Heart, Film, Settings, LogOut, ChevronRight } from 'lucide-react';
import { GENRES } from '../data/movies';

interface ProfileSettingsProps {
  selectedGenres: string[];
  likedMovies: string[];
  onClose: () => void;
  onResetPreferences: () => void;
}

export function ProfileSettings({
  selectedGenres,
  likedMovies,
  onClose,
  onResetPreferences,
}: ProfileSettingsProps) {
  const selectedGenreNames = GENRES.filter((g) => selectedGenres.includes(g.id)).map((g) => g.name);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="absolute right-0 top-0 h-full w-full max-w-md bg-gradient-to-br from-slate-900 to-purple-900 text-white shadow-2xl overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-slate-900/80 backdrop-blur-lg border-b border-white/10 p-6">
          <div className="flex items-center justify-between">
            <h2>Profile & Settings</h2>
            <button
              onClick={onClose}
              className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Profile Section */}
        <div className="p-6">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
              <User className="w-10 h-10" />
            </div>
            <div>
              <h3 className="text-white mb-1">Movie Enthusiast</h3>
              <p className="text-gray-400 text-sm">Member since 2024</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Heart className="w-5 h-5 text-pink-400" />
                <span className="text-gray-400 text-sm">Liked</span>
              </div>
              <div className="text-2xl">{likedMovies.length}</div>
            </div>
            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Film className="w-5 h-5 text-purple-400" />
                <span className="text-gray-400 text-sm">Genres</span>
              </div>
              <div className="text-2xl">{selectedGenres.length}</div>
            </div>
          </div>

          {/* Preferences */}
          <div className="mb-8">
            <h3 className="text-white mb-4">Your Favorite Genres</h3>
            <div className="flex flex-wrap gap-2">
              {selectedGenreNames.map((genre) => (
                <span
                  key={genre}
                  className="px-4 py-2 bg-gradient-to-r from-pink-500/20 to-purple-600/20 border border-purple-500/30 rounded-full text-sm"
                >
                  {genre}
                </span>
              ))}
            </div>
          </div>

          {/* Settings Menu */}
          <div className="space-y-2 mb-8">
            <h3 className="text-white mb-4">Settings</h3>
            
            <button className="w-full flex items-center justify-between p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors border border-white/10">
              <div className="flex items-center gap-3">
                <Settings className="w-5 h-5 text-gray-400" />
                <span>Preferences</span>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>

            <button className="w-full flex items-center justify-between p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors border border-white/10">
              <div className="flex items-center gap-3">
                <Heart className="w-5 h-5 text-gray-400" />
                <span>Liked Movies</span>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>

            <button
              onClick={onResetPreferences}
              className="w-full flex items-center justify-between p-4 bg-white/5 rounded-xl hover:bg-red-500/20 transition-colors border border-white/10 hover:border-red-500/30"
            >
              <div className="flex items-center gap-3">
                <Film className="w-5 h-5 text-gray-400" />
                <span>Reset Preferences</span>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Logout */}
          <button className="w-full flex items-center justify-center gap-2 p-4 bg-red-500/10 rounded-xl hover:bg-red-500/20 transition-colors border border-red-500/20 text-red-400">
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-white/10 text-center text-gray-500 text-sm">
            <p>CineMatch v1.0</p>
            <p className="mt-2">Powered by AI • Made with ❤️</p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
