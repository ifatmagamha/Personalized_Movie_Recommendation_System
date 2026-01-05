export type MovieUI = {
  id: string;          
  movieId: number;     
  title: string;
  year?: number | null;

  genres: string[];
  rating?: number | null;
  description?: string | null;
  duration?: number | null;

  poster?: string | null;
  backdrop?: string | null;


  director?: string | null;
  cast?: string[];
  tags?: string[];
  mood?: string[];
  cinematography?: string | null;

  // debug / UX
  reason?: string | null;
  score?: number | null;
};
