from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ---------- Requests ----------
class RecommendRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="User id for personalized mode (CF)")
    query: str = Field(default="", description="Free text (LLM later / optional)")
    k: int = Field(default=10, ge=1, le=50)
    mode: Literal["baseline", "cf", "auto"] = "auto"
    candidate_pool: int = Field(default=2000, ge=100, le=20000)

    constraints: Optional[Dict[str, Any]] = None
    # Expected keys:
    # {
    #   "genres_in": ["Drama","Comedy"] or ["drama","comedy"],
    #   "genres_out": ["Horror"],
    #   "min_avg_rating": 3.5,
    #   "min_n_ratings": 50,
    #   "exclude_movieIds": [1,2,3]   # avoid already swiped
    # }


class FeedbackRequest(BaseModel):
    user_id: Optional[int] = None
    movieId: int
    action: Literal["like", "dislike", "save", "skip", "helpful", "not_helpful"]
    context: Optional[dict] = None
    # context example:
    # {"mode":"auto","query":"...","constraints":{...},"screen":"results"}


# ---------- Responses ----------
class MovieRecommendation(BaseModel):
    movieId: int
    title: str
    genres: Optional[str] = None
    score: float
    reason: Optional[str] = None

    # enrichment (optional)
    year: Optional[int] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    director: Optional[str] = None
    duration: Optional[int] = None
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    cast: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    mood: Optional[List[str]] = None


class RecommendResponse(BaseModel):
    intent: Dict[str, Any]
    recommendations: List[MovieRecommendation]


class FeedbackResponse(BaseModel):
    status: str
    received: dict


class GenresResponse(BaseModel):
    genres: List[str]
