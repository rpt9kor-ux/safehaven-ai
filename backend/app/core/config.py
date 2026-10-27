import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # Reverted to lowercase so database.py and other files can read them perfectly:
    app_name: str = "SafeHaven HR & Compliance AI"
    database_url: str = "sqlite:///./safehaven.db"
    secret_key: str  # no default on purpose: must come from .env
    access_token_expire_minutes: int = 60
    upload_dir: str = "uploads"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)

settings = Settings()
