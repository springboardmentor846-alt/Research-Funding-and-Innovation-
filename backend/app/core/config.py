"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Research Funding & Innovation Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production-2026-research-platform"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "research_user"
    POSTGRES_PASSWORD: str = "research_pass_2026"
    POSTGRES_DB: str = "research_platform"

    # MongoDB
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "research_platform"
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"

    # OpenRouter AI (replaces OpenAI / HuggingFace / LangChain)
    OPENROUTER_API_KEY: str = "YOUR_API_KEY"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_TIMEOUT_SECONDS: float = 60.0
    OPENROUTER_APP_NAME: str = "Research Funding & Innovation Intelligence Platform"
    OPENROUTER_HTTP_REFERER: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
