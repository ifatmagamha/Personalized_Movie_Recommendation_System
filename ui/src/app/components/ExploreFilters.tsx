import { motion } from "motion/react";
import { ArrowLeft, Plus, Minus } from "lucide-react";
import { useEffect, useState } from "react";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { listGenres } from "@/lib/api";

interface ExploreFiltersProps {
  onApplyFilters: (filters: FilterState) => void;
  onBack: () => void;
}

export interface FilterState {
  selectedGenres: string[];
  excludedGenres: string[];
  minRating: number;
  minPopularity: number;
  isPersonalized: boolean;
}

export function ExploreFilters({ onApplyFilters, onBack }: ExploreFiltersProps) {
  const [availableGenres, setAvailableGenres] = useState<string[]>([]);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [excludedGenres, setExcludedGenres] = useState<string[]>([]);
  const [minRating, setMinRating] = useState([5.0]);
  const [minPopularity, setMinPopularity] = useState([50]);
  const [isPersonalized, setIsPersonalized] = useState(false);

  useEffect(() => {
    listGenres()
      .then((g) => setAvailableGenres(g ?? []))
      .catch(() => setAvailableGenres([]));
  }, []);

  const toggleGenre = (genreName: string, type: "include" | "exclude") => {
    if (type === "include") {
      setExcludedGenres((prev) => prev.filter((x) => x !== genreName));
      setSelectedGenres((prev) =>
        prev.includes(genreName) ? prev.filter((x) => x !== genreName) : [...prev, genreName]
      );
    } else {
      setSelectedGenres((prev) => prev.filter((x) => x !== genreName));
      setExcludedGenres((prev) =>
        prev.includes(genreName) ? prev.filter((x) => x !== genreName) : [...prev, genreName]
      );
    }
  };

  const getGenreState = (genreName: string): "none" | "included" | "excluded" => {
    if (selectedGenres.includes(genreName)) return "included";
    if (excludedGenres.includes(genreName)) return "excluded";
    return "none";
  };

  const handleApply = () => {
    onApplyFilters({
      selectedGenres,
      excludedGenres,
      minRating: minRating[0],
      minPopularity: minPopularity[0],
      isPersonalized,
    });
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 relative overflow-hidden">
      {/* Subtle neon accent background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute top-20 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "7s" }}
        />
        <div
          className="absolute bottom-20 right-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "9s", animationDelay: "1s" }}
        />
      </div>

      {/* Header */}
      <div className="container mx-auto px-6 py-6 relative z-10">
        <button onClick={onBack} className="flex items-center gap-2 text-neutral-400 hover:text-neutral-200 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">back</span>
        </button>
      </div>

      {/* Filters */}
      <div className="container mx-auto px-6 py-12 max-w-4xl relative z-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          {/* Personalized Toggle */}
          <div className="mb-12 pb-12 border-b border-neutral-800">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="mb-2 text-neutral-50">recommendation mode</h3>
                <p className="text-sm text-neutral-400">
                  {isPersonalized ? "personalized recommendations" : "popular with everyone"}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <Label htmlFor="mode-switch" className={`text-sm ${!isPersonalized ? "text-neutral-50" : "text-neutral-500"}`}>
                  popular
                </Label>
                <Switch id="mode-switch" checked={isPersonalized} onCheckedChange={setIsPersonalized} />
                <Label htmlFor="mode-switch" className={`text-sm ${isPersonalized ? "text-neutral-50" : "text-neutral-500"}`}>
                  personalized
                </Label>
              </div>
            </div>
          </div>

          {/* Genre Selection */}
          <div className="mb-12">
            <div className="mb-6">
              <h3 className="mb-2 text-neutral-50">genres</h3>
              <p className="text-sm text-neutral-500">click to include, click again to exclude</p>
            </div>

            <div className="flex flex-wrap gap-3">
              {availableGenres.map((name) => {
                const state = getGenreState(name);
                return (
                  <div key={name} className="relative group">
                    <button
                      onClick={() => toggleGenre(name, "include")}
                      className={`
                        px-5 py-3 rounded-sm text-sm transition-all border
                        ${state === "included"
                          ? "bg-pink-500/20 text-pink-400 border-pink-500/50"
                          : state === "excluded"
                          ? "bg-neutral-800/50 text-neutral-600 border-neutral-700 line-through"
                          : "bg-neutral-900/50 border-neutral-800 text-neutral-400 hover:border-neutral-600"
                        }
                      `}
                    >
                      {name}
                      {state === "included" && <Plus className="inline-block w-3 h-3 ml-1" />}
                      {state === "excluded" && <Minus className="inline-block w-3 h-3 ml-1" />}
                    </button>

                    {state === "included" && (
                      <button
                        onClick={() => toggleGenre(name, "exclude")}
                        className="absolute -top-2 -right-2 w-5 h-5 bg-neutral-800 border border-neutral-700 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Minus className="w-3 h-3 text-neutral-400" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>

            {(selectedGenres.length > 0 || excludedGenres.length > 0) && (
              <button
                onClick={() => {
                  setSelectedGenres([]);
                  setExcludedGenres([]);
                }}
                className="mt-4 text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
              >
                clear all
              </button>
            )}
          </div>

          {/* Rating Slider */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-neutral-50">minimum rating</h3>
              <span className="text-sm text-neutral-400">{minRating[0].toFixed(1)}+</span>
            </div>
            <Slider value={minRating} onValueChange={setMinRating} min={0} max={10} step={0.1} className="w-full" />
            <div className="flex justify-between mt-2 text-xs text-neutral-600">
              <span>0.0</span>
              <span>10.0</span>
            </div>
          </div>

          {/* Popularity Slider (UI-only, backend optional pour l’instant) */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-neutral-50">popularity</h3>
              <span className="text-sm text-neutral-400">{minPopularity[0]}%</span>
            </div>
            <Slider value={minPopularity} onValueChange={setMinPopularity} min={0} max={100} step={5} className="w-full" />
            <div className="flex justify-between mt-2 text-xs text-neutral-600">
              <span>hidden gems</span>
              <span>popular</span>
            </div>
          </div>

          {/* Apply Button */}
          <motion.button
            onClick={handleApply}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full px-8 py-5 bg-transparent border border-pink-500/30 hover:border-pink-500/60 text-neutral-50 transition-all flex items-center justify-center gap-3 backdrop-blur-sm hover:bg-pink-500/5"
          >
            <span>apply filters</span>
            {(selectedGenres.length > 0 || excludedGenres.length > 0) && (
              <span className="text-neutral-500 text-sm">
                ({selectedGenres.length > 0 && `+${selectedGenres.length}`}
                {excludedGenres.length > 0 && ` -${excludedGenres.length}`})
              </span>
            )}
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
