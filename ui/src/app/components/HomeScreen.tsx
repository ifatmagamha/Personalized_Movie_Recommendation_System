import { motion } from "framer-motion";
import { Sparkles, Filter } from "lucide-react";

interface HomeScreenProps {
  onQuickRecommend: () => void;
  onMoodInput: () => void;
}

export function HomeScreen({ onQuickRecommend, onMoodInput }: HomeScreenProps) {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute top-20 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "7s" }}
        />
        <div
          className="absolute bottom-20 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "9s", animationDelay: "1s" }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/5 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "11s", animationDelay: "2s" }}
        />
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-12 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center"
        >
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mb-16"
          >
            <h1 className="text-6xl md:text-7xl font-light mb-6 text-neutral-50">
              what should I watch?
            </h1>
            <p className="text-xl text-neutral-400 max-w-2xl mx-auto">
              discover your next favorite film based on your mood, preferences, or just explore what's popular
            </p>
          </motion.div>

          {/* Action buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="flex flex-col md:flex-row gap-6 justify-center items-center max-w-2xl mx-auto"
          >
            {/* Mood Input */}
            <motion.button
              onClick={onMoodInput}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full md:w-auto px-12 py-6 bg-transparent border-2 border-pink-500/30 hover:border-pink-500/60 text-neutral-50 transition-all flex items-center justify-center gap-4 backdrop-blur-sm hover:bg-pink-500/5 group"
            >
              <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              <span className="text-lg">maybe this</span>
            </motion.button>

            {/* Quick Recommend */}
            <motion.button
              onClick={onQuickRecommend}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full md:w-auto px-12 py-6 bg-transparent border-2 border-blue-500/30 hover:border-blue-500/60 text-neutral-50 transition-all flex items-center justify-center gap-4 backdrop-blur-sm hover:bg-blue-500/5 group"
            >
              <Filter className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              <span className="text-lg">explore with filters</span>
            </motion.button>
          </motion.div>

          {/* Footer hint */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-16 text-sm text-neutral-500"
          >
            type how you feel • speak what you need • we'll find something
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
