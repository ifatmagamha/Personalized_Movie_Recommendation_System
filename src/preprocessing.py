from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from google.cloud import bigquery

from .config import SOURCE_PROJECT, SOURCE_DATASET


@dataclass
class BQTables:
    ratings: str = f"`{SOURCE_PROJECT}.{SOURCE_DATASET}.ratings`"
    movies: str = f"`{SOURCE_PROJECT}.{SOURCE_DATASET}.movies`"


def _run_df(client: bigquery.Client, sql: str) -> pd.DataFrame:
    """Run a SELECT query and return a DataFrame."""
    return client.query(sql).to_dataframe()


def get_ratings_sample(client: bigquery.Client, limit: int = 100) -> pd.DataFrame:
    t = BQTables()
    sql = f"""
    SELECT userId, movieId, rating, timestamp
    FROM {t.ratings}
    LIMIT {limit}
    """
    return _run_df(client, sql)


def get_movie_stats(client: bigquery.Client, min_ratings: int = 0, limit: Optional[int] = 100) -> pd.DataFrame:
    """
    Compute per-movie stats.
    min_ratings: filter to movies with at least N ratings (stability).
    """
    t = BQTables()
    lim = f"LIMIT {limit}" if limit is not None else ""
    sql = f"""
    WITH movie_stats AS (
      SELECT
        movieId,
        COUNT(*) AS n_ratings,
        AVG(rating) AS avg_rating,
        STDDEV(rating) AS std_rating
      FROM {t.ratings}
      WHERE rating IS NOT NULL
      GROUP BY movieId
    )
    SELECT *
    FROM movie_stats
    WHERE n_ratings >= {min_ratings}
    ORDER BY n_ratings DESC
    {lim}
    """
    return _run_df(client, sql)


def get_user_stats(client: bigquery.Client, min_ratings: int = 0, limit: Optional[int] = 100) -> pd.DataFrame:
    """Compute per-user stats."""
    t = BQTables()
    lim = f"LIMIT {limit}" if limit is not None else ""
    sql = f"""
    WITH user_stats AS (
      SELECT
        userId,
        COUNT(*) AS n_ratings,
        AVG(rating) AS avg_rating,
        MIN(timestamp) AS first_ts,
        MAX(timestamp) AS last_ts
      FROM {t.ratings}
      WHERE rating IS NOT NULL
      GROUP BY userId
    )
    SELECT *
    FROM user_stats
    WHERE n_ratings >= {min_ratings}
    ORDER BY n_ratings DESC
    {lim}
    """
    return _run_df(client, sql)


def get_interactions(client: bigquery.Client, min_user_ratings: int = 0, min_movie_ratings: int = 0,
                     limit: Optional[int] = 10000) -> pd.DataFrame:
    """
    Build interactions dataset (userId, movieId, rating, timestamp) with optional filtering.
    """
    t = BQTables()
    lim = f"LIMIT {limit}" if limit is not None else ""
    sql = f"""
    WITH base AS (
      SELECT userId, movieId, rating, timestamp
      FROM {t.ratings}
      WHERE rating IS NOT NULL
    ),
    user_counts AS (
      SELECT userId, COUNT(*) AS n_user
      FROM base
      GROUP BY userId
    ),
    movie_counts AS (
      SELECT movieId, COUNT(*) AS n_movie
      FROM base
      GROUP BY movieId
    ),
    filtered AS (
      SELECT b.*
      FROM base b
      JOIN user_counts u USING(userId)
      JOIN movie_counts m USING(movieId)
      WHERE u.n_user >= {min_user_ratings}
        AND m.n_movie >= {min_movie_ratings}
    )
    SELECT *
    FROM filtered
    {lim}
    """
    return _run_df(client, sql)


def get_movies_metadata(client: bigquery.Client, limit: Optional[int] = None) -> pd.DataFrame:
    """Fetch movies metadata (viewer-safe)."""
    t = BQTables()
    lim = f"LIMIT {limit}" if limit is not None else ""
    sql = f"""
    SELECT movieId, title, genres
    FROM {t.movies}
    {lim}
    """
    return _run_df(client, sql)
