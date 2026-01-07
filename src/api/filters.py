from typing import List, Optional, Iterable
import pandas as pd


def _split_genres(genres: str) -> List[str]:
    if not isinstance(genres, str) or not genres.strip():
        return []
    # support with or without |
    parts = [g.strip().lower() for g in genres.split("|")]
    return [p for p in parts if p]

def apply_filters(
    df: pd.DataFrame,
    include_genres: Optional[Iterable[str]] = None,
    exclude_genres: Optional[Iterable[str]] = None,
    min_n_ratings: Optional[int] = None,
    min_avg_rating: Optional[float] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    exclude_movieIds: Optional[Iterable[int]] = None,
) -> pd.DataFrame:
    out = df.copy()

    # Year filters
    if "year" in out.columns:
        if min_year is not None:
            out = out[out["year"] >= int(min_year)]
        if max_year is not None:
            out = out[out["year"] <= int(max_year)]

    # exclude already swiped
    if exclude_movieIds and "movieId" in out.columns:
        out = out[~out["movieId"].isin(list(exclude_movieIds))]

    # stats filters (if present)
    if min_n_ratings is not None and "n_ratings" in out.columns:
        out = out[out["n_ratings"] >= int(min_n_ratings)]

    if min_avg_rating is not None and "avg_rating" in out.columns:
        out = out[out["avg_rating"] >= float(min_avg_rating)]

    # genre include/exclude (works with "Drama|Western" or "Western")
    inc = set(g.lower() for g in (include_genres or []) if isinstance(g, str) and g.strip())
    exc = set(g.lower() for g in (exclude_genres or []) if isinstance(g, str) and g.strip())

    if "genres" in out.columns and (inc or exc):
        if exc:
            out = out[~out["genres"].apply(lambda x: any(g in exc for g in _split_genres(x)))]
        if inc:
            out = out[out["genres"].apply(lambda x: any(g in inc for g in _split_genres(x)))]

    return out
