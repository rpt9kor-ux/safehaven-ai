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

    # Vector database: empty qdrant_url = local folder mode; set it to use a Qdrant server
    qdrant_url: str | None = None
    qdrant_path: str = "qdrant_data"
    qdrant_collection: str = "policy_chunks"

    # Embedding model (384-dimension vectors)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    model_cache_dir: str = "models_cache"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)

    # LLM (Google Gemini free tier)
    gemini_api_key: str | None = None
    llm_model: str = "gemini-2.5-flash"

settings = Settings()
