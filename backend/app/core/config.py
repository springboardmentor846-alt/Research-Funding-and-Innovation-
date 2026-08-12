"""
Application Settings & Environment Configuration (Pydantic v2)
"""

from typing import List, Union
from pydantic import Field, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.constants import Environment, API_V1_STR, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core System Settings
    PROJECT_NAME: str = "Research Funding & Innovation Intelligence Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = API_V1_STR
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security & JWT Tokens
    SECRET_KEY: str = Field(
        default="SUPER_SECRET_TEMPORARY_DEVELOPMENT_KEY_MUST_BE_CHANGED_IN_PRODUCTION_32BYTES",
        description="Master secret key for JWT token signing"
    )
    ALGORITHM: str = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS: int = REFRESH_TOKEN_EXPIRE_DAYS

    # CORS Allowed Origins
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    # Database Settings (PostgreSQL - Async SQLAlchemy 2.0)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "funding_platform"
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./funding_platform.db",
        description="Async SQLAlchemy connection string (SQLite fallback or PostgreSQL)"
    )

    # Connection Pool Tweaks
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis Cache & Message Broker
    REDIS_URL: str = "redis://localhost:6379/0"

    # MongoDB Document Database
    MONGO_URI: str = "mongodb://admin:mongo_password@localhost:27017"
    MONGO_DB_NAME: str = "funding_unstructured_docs"

    # Vector DB (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Union[str, None] = None


# Instantiate singleton settings instance
settings = Settings()
