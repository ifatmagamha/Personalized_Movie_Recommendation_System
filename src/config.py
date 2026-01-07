import os
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path.cwd().parent   
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


# Source dataset (read-only)
SOURCE_PROJECT = os.getenv("SOURCE_PROJECT", "master-ai-cloud")
SOURCE_DATASET = os.getenv("SOURCE_DATASET", "MoviePlatform")

# Work project/dataset (write if permissions allow)
WORK_PROJECT = os.getenv("WORK_PROJECT", "students-group1")
WORK_DATASET = os.getenv("WORK_DATASET", "movie_reco")

DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "10000"))  # for safe exploration


PROJECT_ROOT = Path.cwd().parent   
DATA_DIR = PROJECT_ROOT / "data"