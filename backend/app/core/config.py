from functools import lru_cache
import os
from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    APP_NAME: str = "Recetario"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API
    API_PREFIX: str = "/api"

    # Security & CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3041",
        "http://127.0.0.1:3041",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "recetario"
    POSTGRES_PASSWORD: str = "recetario_secret"
    POSTGRES_DB: str = "recetario"
    DATABASE_URL: Union[str, None] = None

    # Database Pool Settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    # Uploads (Persistent storage for recipe media)
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./uploads"))

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins whether supplied as JSON array or comma-separated string."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            val = self.CORS_ORIGINS.strip()
            if val.startswith("[") and val.endswith("]"):
                try:
                    import json
                    return json.loads(val)
                except Exception:
                    pass
            return [origin.strip() for origin in val.split(",") if origin.strip()]
        return []


    @property
    def sync_database_url(self) -> str:
        """Return the SQLAlchemy-compatible database connection URL."""
        if self.DATABASE_URL:
            # Normalize legacy postgresql:// to modern postgresql+psycopg://
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Dependency provider for cached application settings."""
    return Settings()
