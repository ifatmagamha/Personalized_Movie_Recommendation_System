import type { MovieRec } from "@/lib/api";
import type { MovieUI } from "@/app/types";

function splitGenres(genres?: string | null): string[] {
  if (!genres) return [];
  const g = genres.trim();
  if (!g) return [];
  if (g.includes("|")) return g.split("|").map(s => s.trim()).filter(Boolean);
  if (g.includes(",")) return g.split(",").map(s => s.trim()).filter(Boolean);
  return [g];
}

// fallback image ( avoid broken images)
const FALLBACK_POSTER =
  "data:image/svg+xml;charset=utf-8," +
  encodeURIComponent(`
  <svg xmlns="http://www.w3.org/2000/svg" width="600" height="900">
    <rect width="100%" height="100%" fill="#111827"/>
    <text x="50%" y="50%" fill="#9CA3AF" font-size="28" text-anchor="middle" font-family="Arial">
      No poster
    </text>
  </svg>
`);

export function mapMovieRecToUI(m: MovieRec): MovieUI {
  // Handle poster: use fallback if null, undefined, or empty string
  const poster = (m.poster && m.poster.trim().length > 0) ? m.poster : FALLBACK_POSTER;
  
  return {
    id: String(m.movieId),
    movieId: m.movieId,
    title: m.title || `Movie ${m.movieId}`, // Fallback title if missing
    year: m.year ?? null,

    genres: splitGenres(m.genres),
    rating: m.rating ?? null,
    description: m.description ?? null,
    duration: m.duration ?? null,

    poster: poster,
    backdrop: m.backdrop ?? null,

    // defaults ui-safe
    director: null,
    cast: [],
    tags: [],
    mood: [],
    cinematography: null,

    reason: m.reason ?? null,
    score: (m as any).score ?? null, 
  };
}
