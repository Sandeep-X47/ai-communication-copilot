"""Central configuration, read from environment variables."""
import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        # Database (SQLite by default; set DATABASE_URL for Postgres)
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./copilot.db")

        # Auth
        self.jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
        self.jwt_algorithm: str = "HS256"
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
        )

        # LLM (OpenAI-compatible; empty key => offline mock)
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.use_mock_llm: bool = not bool(self.openai_api_key)

        # Redis (cache, rate limit, analytics counters; empty => in-memory)
        self.redis_url: str = os.getenv("REDIS_URL", "")

        # Limits / CORS
        self.rate_limit_per_day: int = int(os.getenv("RATE_LIMIT_PER_DAY", "100"))
        self.cors_origins: list[str] = os.getenv(
            "CORS_ORIGINS", "http://localhost:5173"
        ).split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()
