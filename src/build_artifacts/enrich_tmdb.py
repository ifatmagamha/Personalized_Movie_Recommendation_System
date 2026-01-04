from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests

from dotenv import load_dotenv
load_dotenv()

TMDB_BEARER = os.getenv("TMDB_BEARER")
assert TMDB_BEARER, "TMDB_BEARER missing"


TMDB_API = "https://api.themoviedb.org/3"


def extract_release_year(df: pd.DataFrame, title_col: str = "title") -> pd.DataFrame:
    df = df.copy()
    df["year"] = (
        df[title_col]
        .astype(str)
        .str.extract(r"\((\d{4})\)")
        .astype("float")
        .astype("Int64")
    )
    df["title_clean"] = (
        df[title_col]
        .astype(str)
        .str.replace(r"\s*\(\d{4}\)", "", regex=True)
        .str.strip()
    )
    return df


class TMDBClient:
    def __init__(self, bearer: str, timeout: int = 20):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "Authorization": f"Bearer {bearer}",
        })
        self.timeout = timeout
        self._config: Optional[Dict[str, Any]] = None

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{TMDB_API}{path}"
        r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def config(self) -> dict:
        if self._config is None:
            self._config = self._get("/configuration")
        return self._config

    
    def image_url(self, file_path: Optional[str], kind: str = "poster") -> Optional[str]:
        if not file_path or not isinstance(file_path, str):
            return None

        if not file_path.startswith("/"):
            file_path = "/" + file_path

        cfg = self.config()
        base = cfg["images"]["secure_base_url"]  # https://image.tmdb.org/t/p/
        size = "w500" if kind == "poster" else "w780"
        return f"{base}{size}{file_path}"

    def search_movie(self, title: str, year: Optional[int]) -> Optional[dict]:
        params = {"query": title, "include_adult": "false", "language": "en-US"}
        if year and not pd.isna(year):
            params["year"] = int(year)
        data = self._get("/search/movie", params=params)
        results = data.get("results", [])
        return results[0] if results else None

    def movie_details(self, tmdb_id: int) -> dict:
        # append credits si tu veux cast/director plus tard
        return self._get(f"/movie/{tmdb_id}", params={"language": "en-US"})


def choose_tmdb_match(title_clean: str, year: Optional[int], candidate: Optional[dict]) -> Optional[int]:
    if not candidate:
        return None
    return int(candidate["id"])


def enrich_movies(
    movies_path: str = "data/movies.parquet",
    out_path: str = "data/movies_enriched.parquet",
    mapping_path: str = "data/tmdb_mapping.parquet",
    sleep_s: float = 0.30,  # respecter la limite
    limit: Optional[int] = 200,
    debug: bool = False,
) -> None:
    bearer = os.environ.get("TMDB_BEARER")
    if not bearer:
        raise RuntimeError("Missing env var TMDB_BEARER (TMDB v4 Bearer token).")

    df = pd.read_parquet(movies_path)
    df = extract_release_year(df)

    # mapping stable movieId -> tmdb_id (évite rematch à chaque run)
    if os.path.exists(mapping_path):
        map_df = pd.read_parquet(mapping_path)
        mapping = dict(zip(map_df["movieId"].astype(int), map_df["tmdb_id"].astype("Int64")))
    else:
        mapping = {}

    client = TMDBClient(bearer=bearer)

    # colonnes enrichies (ne pas override si déjà présentes)
    for col in ["tmdb_id", "description", "poster", "backdrop", "rating", "duration"]:
        if col not in df.columns:
            df[col] = pd.NA

    updated = 0

    for idx, (i, row) in enumerate (df.iterrows()):
        if limit is not None and idx >= limit:
            break
            
        mid = int(row["movieId"])
        title_clean = str(row["title_clean"])
        year = row.get("year", pd.NA)

        tmdb_id = mapping.get(mid)
        if pd.isna(tmdb_id) or tmdb_id is None:
            cand = client.search_movie(title_clean, None if pd.isna(year) else int(year))
            tmdb_id = choose_tmdb_match(title_clean, year, cand)
            if tmdb_id:
                mapping[mid] = tmdb_id

        if not tmdb_id:
            continue

        # anti-override: si déjà enrichi, skip
        if pd.notna(df.at[i, "poster"]) and pd.notna(df.at[i, "description"]):
            continue

        try:
            details = client.movie_details(int(tmdb_id))
        except Exception:
            continue
            
        if debug and updated < 5:
            print(
            f"[DEBUG] movieId={mid} tmdb_id={tmdb_id} "
            f"poster_path={details.get('poster_path')} "
            f"backdrop_path={details.get('backdrop_path')}"
            )


        # fill only if missing
        if pd.isna(df.at[i, "description"]):
            df.at[i, "description"] = details.get("overview")
        if pd.isna(df.at[i, "rating"]):
            df.at[i, "rating"] = details.get("vote_average")
        if pd.isna(df.at[i, "duration"]):
            df.at[i, "duration"] = details.get("runtime")

        if pd.isna(df.at[i, "poster"]):
            df.at[i, "poster"] = client.image_url(details.get("poster_path"), "poster")
        if pd.isna(df.at[i, "backdrop"]):
            df.at[i, "backdrop"] = client.image_url(details.get("backdrop_path"), "backdrop")

        df.at[i, "tmdb_id"] = int(tmdb_id)
        updated += 1

        time.sleep(sleep_s)

    # sauver mapping stable
    map_out = pd.DataFrame({
        "movieId": list(mapping.keys()),
        "tmdb_id": [mapping[k] for k in mapping.keys()],
    })
    map_out.to_parquet(mapping_path, index=False)

    # NB: title = title_clean pour UI 
    df["title"] = df["title_clean"]

    keep_cols = [c for c in [
        "movieId", "title", "genres", "year",
        "tmdb_id", "description", "poster", "backdrop",
        "rating", "duration"
    ] if c in df.columns]

    df[keep_cols].to_parquet(out_path, index=False)
    print(f"Enriched saved to {out_path} | updated rows: {updated}")


if __name__ == "__main__":
    enrich_movies(limit=None, debug=False)
