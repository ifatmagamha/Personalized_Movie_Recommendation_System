from functools import lru_cache
from src.predictions import load_recommender, Recommender

@lru_cache(maxsize=1)
def get_recommender() -> Recommender:
    # charge une seule fois (artifacts + cf_model + movies.parquet)
    return load_recommender(models_dir="models", interactions_path="data/interactions.parquet")
