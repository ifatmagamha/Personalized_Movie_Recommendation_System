from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import json

# #region agent log
log_path = r"c:\Users\islem\Downloads\M2\cloud\projet\Personalized_Movie_Recommendation_System\.cursor\debug.log"
def _log(hypothesis_id, location, message, data):
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":hypothesis_id,"location":location,"message":message,"data":data,"timestamp":int(__import__("time").time()*1000)})+"\n")
    except: pass
# #endregion

class Settings(BaseSettings):
    APP_NAME: str = "Movie Rec API"
    ENV: str = "dev"
    ROOT_PATH: str = ""
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env" if os.path.exists(".env") else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
        extra="ignore",  # Ignore extra fields from .env (like TMDB_BEARER, TMDB_API_KEY)
    )

# #region agent log
_log("A", "settings.py:28", "Before Settings() instantiation", {"env_exists": os.path.exists(".env"), "tmdb_bearer_in_env": "TMDB_BEARER" in os.environ, "tmdb_api_key_in_env": "TMDB_API_KEY" in os.environ})
# #endregion

try:
    settings = Settings()
    # #region agent log
    _log("B", "settings.py:32", "Settings() instantiation succeeded", {"cors_origins": settings.CORS_ORIGINS})
    # #endregion
except Exception as e:
    # #region agent log
    _log("C", "settings.py:35", "Settings() instantiation failed", {"error_type": type(e).__name__, "error_msg": str(e)})
    # #endregion
    raise
