export interface Movie {
  id: string;            
  title: string;
  year?: number;
  genres: string[];
  rating?: number;
  description?: string;
  poster?: string;
  backdrop?: string;
  duration?: number;
  reason?: string;
}
