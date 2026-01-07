export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export type RecommendMode = "baseline" | "cf" | "auto";

export type RecommendRequest = {
  user_id?: number | null;
  query?: string;
  k?: number;
  mode?: RecommendMode;
  candidate_pool?: number;
  constraints?: {
    genres_in?: string[];
    genres_out?: string[];
    min_avg_rating?: number;
    min_n_ratings?: number;
    exclude_movieIds?: number[];
  };
};

export type MovieRec = {
  movieId: number;
  title: string;
  genres?: string | null;
  score: number;
  reason?: string | null;

  year?: number | null;
  rating?: number | null;
  description?: string | null;
  duration?: number | null;
  poster?: string | null;
  backdrop?: string | null;
};

export async function recommend(payload: RecommendRequest) {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // credentials: "include", // active si besoin plus tard
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`recommend failed: ${res.status}`);
  return (await res.json()) as { intent: any; recommendations: MovieRec[] };
}

export async function listGenres() {
  const res = await fetch(`${API_BASE}/genres`, {
    // credentials: "include",
  });
  if (!res.ok) throw new Error(`genres failed: ${res.status}`);
  const data = (await res.json()) as { genres: string[] };
  return data.genres ?? [];
}

export async function sendFeedback(payload: {
  user_id?: number | null;
  movieId: number;
  action: "like" | "dislike" | "save" | "skip" | "helpful" | "not_helpful";
  context?: any;
}) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`feedback failed: ${res.status}`);
  return await res.json();
}
