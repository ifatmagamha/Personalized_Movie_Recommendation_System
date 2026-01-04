from __future__ import annotations

import os
import time
import random
from typing import Any, Dict, Optional, Iterable, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_BEARER = os.getenv("TMDB_BEARER")
if not TMDB_BEARER:
    raise RuntimeError("TMDB_BEARER missing in .env (TMDB v4 Bearer token)")

TMDB_API = "https://api.themoviedb.org/3"


def extract_release_year(df: pd.DataFrame, title_col: str = "title") -> pd.DataFrame:
    df = df.copy()
    df["title_raw"] = df[title_col].astype(str)

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


def now_s() -> float:
    return time.time()


class TMDBClient:
    def __init__(self, bearer: str, timeout: int = 25):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "Authorization": f"Bearer {bearer}",
        })
        self.timeout = timeout
        self._config: Optional[Dict[str, Any]] = None

    def _get(self, path: str, params: Optional[dict] = None, max_retries: int = 6) -> dict:
        """
        Robust GET:
        - Retry on 429 / transient errors
        """
        url = f"{TMDB_API}{path}"
        backoff = 0.8

        for attempt in range(max_retries):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)

                # Rate limit
                if r.status_code == 429:
                    retry_after = r.headers.get("Retry-After")
                    sleep_t = float(retry_after) if retry_after else backoff * (2 ** attempt)
                    sleep_t = min(30.0, sleep_t) + random.uniform(0, 0.2)
                    time.sleep(sleep_t)
                    continue

                r.raise_for_status()
                return r.json()

            except requests.RequestException:
                sleep_t = min(20.0, backoff * (2 ** attempt)) + random.uniform(0, 0.2)
                time.sleep(sleep_t)

        raise RuntimeError(f"TMDB request failed after retries: {url}")

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
        if year is not None:
            params["year"] = int(year)

        data = self._get("/search/movie", params=params)
        results = data.get("results", [])
        return results[0] if results else None

    def movie_details(self, tmdb_id: int) -> dict:
        return self._get(f"/movie/{tmdb_id}", params={"language": "en-US"})


def choose_tmdb_match(candidate: Optional[dict]) -> Optional[int]:
    if not candidate:
        return None
    return int(candidate["id"])


# Validation 

def head_ok(url: str, timeout: int = 10) -> bool:
    """
    Validate that the image URL exists.
    Use HEAD (lightweight). Some CDNs may block HEAD; fallback to GET range if needed.
    """
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return True
        # fallback if HEAD not supported
        if r.status_code in (403, 405):
            r2 = requests.get(url, timeout=timeout, stream=True)
            return r2.status_code == 200
        return False
    except requests.RequestException:
        return False


# Main enrichment

def enrich_movies(
    movies_path: str = "data/movies.parquet",
    out_path: str = "data/enriched_data.parquet",
    mapping_path: str = "data/tmdb_mapping_v2.parquet",

    # rate limiting / pacing
    sleep_s: float = 0.30,     # base pacing to stay safe
    max_items: Optional[int] = None,  # None = all

    # checkpointing
    checkpoint_every: int = 500,

    # validation sampling
    validate_every: int = 500,     # validate 1 poster every N updates
    debug_first: int = 5,
) -> None:
    client = TMDBClient(bearer=TMDB_BEARER)

    # Load base movies
    df = pd.read_parquet(movies_path)
    df = extract_release_year(df, title_col="title")

    # Resume: if out_path exists, load it and merge (prefer enriched values)
    if os.path.exists(out_path):
        enriched_prev = pd.read_parquet(out_path)
        # merge on movieId, keep new columns from prev if present
        df = df.merge(enriched_prev.drop(columns=[c for c in ["title", "genres", "year"] if c in enriched_prev.columns], errors="ignore"),
                      on="movieId", how="left", suffixes=("", "_prev"))

    # Load mapping stable movieId -> tmdb_id
    mapping: Dict[int, Optional[int]] = {}
    if os.path.exists(mapping_path):
        map_df = pd.read_parquet(mapping_path)
        if "movieId" in map_df.columns and "tmdb_id" in map_df.columns:
            mapping = {int(k): (None if pd.isna(v) else int(v)) for k, v in zip(map_df["movieId"], map_df["tmdb_id"])}

    # Ensure columns exist
    needed_cols = ["tmdb_id", "description", "poster", "backdrop", "rating", "duration"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # IMPORTANT: Use clean title for UI but keep raw
    # We'll write final `title` as title_clean in output.
    # title_raw remains for debugging.
    total = len(df)
    t0 = now_s()
    last_log = t0

    updated = 0
    matched = 0
    skipped_already = 0
    not_found = 0
    errors = 0
    validated_ok = 0
    validated_bad = 0

    # For safety: operate on a deterministic order
    df = df.sort_values("movieId").reset_index(drop=True)

    for idx, row in df.iterrows():
        if max_items is not None and idx >= int(max_items):
            break

        mid = int(row["movieId"])
        title_clean = str(row.get("title_clean", "")).strip()
        year = row.get("year", pd.NA)
        year_int = None if pd.isna(year) else int(year)

        # skip if already enriched (anti-override)
        has_core = pd.notna(row.get("poster")) and pd.notna(row.get("description"))
        if has_core:
            skipped_already += 1
            continue

        tmdb_id = mapping.get(mid)

        # search if missing tmdb_id
        if tmdb_id is None:
            try:
                cand = client.search_movie(title_clean, year_int)
                tmdb_id = choose_tmdb_match(cand)
                mapping[mid] = tmdb_id  # can be None too (cache miss)
            except Exception:
                errors += 1
                continue

        if not tmdb_id:
            not_found += 1
            continue

        matched += 1

        # details
        try:
            details = client.movie_details(int(tmdb_id))
        except Exception:
            errors += 1
            continue

        if updated < debug_first:
            print(
                f"[DEBUG] movieId={mid} tmdb_id={tmdb_id} "
                f"poster_path={details.get('poster_path')} "
                f"backdrop_path={details.get('backdrop_path')}"
            )

        # Fill only missing values
        if pd.isna(df.at[idx, "description"]):
            df.at[idx, "description"] = details.get("overview")
        if pd.isna(df.at[idx, "rating"]):
            df.at[idx, "rating"] = details.get("vote_average")
        if pd.isna(df.at[idx, "duration"]):
            df.at[idx, "duration"] = details.get("runtime")

        if pd.isna(df.at[idx, "poster"]):
            df.at[idx, "poster"] = client.image_url(details.get("poster_path"), "poster")
        if pd.isna(df.at[idx, "backdrop"]):
            df.at[idx, "backdrop"] = client.image_url(details.get("backdrop_path"), "backdrop")

        df.at[idx, "tmdb_id"] = int(tmdb_id)
        updated += 1

        # light validation sampling
        if updated % validate_every == 0:
            poster_url = df.at[idx, "poster"]
            if isinstance(poster_url, str) and poster_url.startswith("http"):
                ok = head_ok(poster_url)
                if ok:
                    validated_ok += 1
                else:
                    validated_bad += 1

        # progress log every 200 processed rows
        if idx % 200 == 0 and idx > 0:
            now = now_s()
            dt = now - last_log
            if dt > 0:
                rate = 200 / dt
                elapsed = (now - t0) / 60
                remaining = ((total - idx) / max(rate, 1e-9)) / 60
                print(
                    f"[PROGRESS] {idx}/{total} | updated={updated} | "
                    f"skipped={skipped_already} | not_found={not_found} | errors={errors} | "
                    f"{rate:.2f} rows/s | elapsed={elapsed:.1f}m | ETA={remaining:.1f}m"
                )
            last_log = now

        # checkpoint
        if updated > 0 and updated % checkpoint_every == 0:
            _save_outputs(df, mapping, out_path, mapping_path)
            print(f"[CHECKPOINT] saved at updated={updated}")

        # pacing
        time.sleep(sleep_s)

    # final save
    _save_outputs(df, mapping, out_path, mapping_path)

    print(
        f"[DONE] saved {out_path}\n"
        f"updated={updated} matched={matched} skipped_already={skipped_already} "
        f"not_found={not_found} errors={errors}\n"
        f"url_validation: ok={validated_ok} bad={validated_bad} (sampled)"
    )


def _save_outputs(df: pd.DataFrame, mapping: Dict[int, Optional[int]], out_path: str, mapping_path: str) -> None:
    # Save mapping stable
    map_out = pd.DataFrame({
        "movieId": list(mapping.keys()),
        "tmdb_id": [mapping[k] if mapping[k] is not None else pd.NA for k in mapping.keys()],
    })
    map_out.to_parquet(mapping_path, index=False)

    # Title normalization for UI
    df_out = df.copy()
    df_out["title"] = df_out["title_clean"]

    keep_cols = [
        "movieId", "title", "genres", "year",
        "tmdb_id", "description", "poster", "backdrop",
        "rating", "duration",
        "title_raw"  # optional but useful
    ]
    keep_cols = [c for c in keep_cols if c in df_out.columns]
    df_out[keep_cols].to_parquet(out_path, index=False)


if __name__ == "__main__":
    enrich_movies(
        max_items=None,          
        sleep_s=0.30,
        checkpoint_every=500,
        validate_every=500,
        debug_first=5,
    )
