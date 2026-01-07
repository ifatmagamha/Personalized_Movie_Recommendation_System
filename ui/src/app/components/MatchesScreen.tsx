
import { motion } from "framer-motion";
import { ArrowLeft, Play, Info } from "lucide-react";
import type { MovieUI } from "@/app/types";

interface MatchesScreenProps {
    movies: MovieUI[];
    suggestedRecommendations?: MovieUI[];
    onBack: () => void;
    onSelectMovie: (movie: MovieUI) => void;
}

export function MatchesScreen({ movies, suggestedRecommendations = [], onBack, onSelectMovie }: MatchesScreenProps) {
    return (
        <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden pb-20">
            {/* Background Orbs */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-20 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
            </div>

            <div className="container mx-auto px-6 py-6 border-b border-neutral-800 relative z-10 flex items-center justify-between">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-neutral-400 hover:text-neutral-200 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    <span className="text-sm">back to swiping</span>
                </button>
                <h1 className="text-lg font-medium bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Your Matches
                </h1>
                <div className="w-20" />
            </div>

            <div className="container mx-auto px-6 py-12 relative z-10">
                {movies.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-neutral-500 italic">No matches yet. Keep swiping!</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {movies.map((movie, idx) => (
                            <motion.div
                                key={movie.movieId}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className="group relative bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-2xl hover:border-purple-500/50 transition-all"
                            >
                                <div className="relative aspect-[2/3] overflow-hidden">
                                    <img
                                        src={movie.poster || "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=800"}
                                        alt={movie.title}
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-transparent to-transparent opacity-60" />

                                    <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-md px-3 py-1 text-xs rounded-full">
                                        {movie.year}
                                    </div>
                                </div>

                                <div className="p-6">
                                    <h3 className="text-xl font-semibold mb-2 group-hover:text-purple-400 transition-colors">
                                        {movie.title}
                                    </h3>
                                    <div className="flex flex-wrap gap-2 mb-4">
                                        {(movie.genres || []).slice(0, 3).map(g => (
                                            <span key={g} className="text-[10px] uppercase tracking-tighter px-2 py-0.5 border border-neutral-700 rounded text-neutral-400">
                                                {g}
                                            </span>
                                        ))}
                                    </div>

                                    {movie.reason && (
                                        <p className="text-xs text-neutral-500 italic mb-6 line-clamp-2">
                                            "{movie.reason}"
                                        </p>
                                    )}

                                    <div className="flex items-center gap-3">
                                        <button
                                            onClick={() => onSelectMovie(movie)}
                                            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-sm rounded-lg transition-colors border border-neutral-700"
                                        >
                                            <Info className="w-4 h-4" />
                                            Details
                                        </button>
                                        <button className="p-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg transition-all shadow-lg shadow-purple-500/20">
                                            <Play className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}

                {suggestedRecommendations.length > 0 && (
                    <div className="mt-20">
                        <h2 className="text-xl font-medium mb-8 text-neutral-300 flex items-center gap-3">
                            <span className="w-8 h-[1px] bg-neutral-800"></span>
                            Top Suggestions for You
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {suggestedRecommendations.slice(0, 4).map((movie, idx) => (
                                <div
                                    key={movie.movieId}
                                    onClick={() => onSelectMovie(movie)}
                                    className="bg-neutral-900/40 border border-neutral-800 p-4 rounded-lg hover:border-neutral-600 transition-colors cursor-pointer flex gap-4 items-center"
                                >
                                    <img src={movie.poster || ""} alt="" className="w-12 h-18 object-cover rounded shadow" />
                                    <div>
                                        <h4 className="text-sm font-medium line-clamp-1">{movie.title}</h4>
                                        <p className="text-[10px] text-neutral-500">{movie.year}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
