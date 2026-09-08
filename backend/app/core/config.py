"""
Central app configuration, loaded from environment variables.
Copy .env.example to .env and fill in real values before running.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

# Load variables from a .env file in the backend/ directory into the
# process environment. Without this call, os.getenv() below would only
# ever see real OS-level environment variables, never anything from .env
# — which is why editing .env alone wasn't taking effect.
load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/triage_db"
    )

    # LLM provider (provider-agnostic wrapper reads these)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")  # "anthropic" | "openai"
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

    # Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12  # 12 hours
    REPORT_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REPORT_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    AUTO_CREATE_TABLES: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"

    # RAG / vector store
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./chroma_store")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # App
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES = ["en", "de"]

    def validate(self) -> None:
        if self.ENVIRONMENT.lower() in {"production", "prod"}:
            if self.JWT_SECRET == "change-this-in-production" or len(self.JWT_SECRET) < 32:
                raise RuntimeError("JWT_SECRET must be a long random value in production")
            if self.FRONTEND_ORIGIN.startswith("http://localhost"):
                raise RuntimeError("FRONTEND_ORIGIN must use the deployed HTTPS origin in production")
            if not self.LLM_API_KEY:
                raise RuntimeError("LLM_API_KEY is required in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
