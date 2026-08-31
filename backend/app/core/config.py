"""
AI Chargeback Guardian — Core Configuration

Loads settings from environment variables / .env file using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_FILE = _BACKEND_DIR / "chargeback_guardian.db"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "AI Chargeback Guardian"

    # Database
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_DB_FILE.as_posix()}"

    @property
    def canonical_db_path(self) -> Path:
        return _DEFAULT_DB_FILE

    # LLM
    LLM_PROVIDER: str = "demo"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
# If DATABASE_URL was loaded as a relative sqlite path from .env, resolve it to canonical DB path
if settings.DATABASE_URL.startswith("sqlite:///.") or settings.DATABASE_URL == "sqlite:///chargeback_guardian.db":
    settings.DATABASE_URL = f"sqlite:///{_DEFAULT_DB_FILE.as_posix()}"

