"""Application settings.

Loaded from environment variables (and an optional .env file). Field names map
case-insensitively to env vars, so `database_url` reads `DATABASE_URL`, etc.
See https://fastapi.tiangolo.com/advanced/settings/
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Primary connection. Default matches docker-compose so the app boots
    # before any DB env is provided (Phase 1 has no DB logic yet).
    database_url: str = "postgresql://postgres:postgres@api-db:5432/hive_dev"
    # Optional override used by the test suite / CI (which only sets this).
    database_test_url: str | None = None
    testing: bool = False
    environment: str = "dev"

    # JWT settings. The secret has a dev default so tests/CI run without setup;
    # it MUST be overridden via JWT_SECRET_KEY in production.
    jwt_secret_key: str = "dev-only-insecure-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    @property
    def active_database_url(self) -> str:
        """The DB URL to actually use: the test URL when testing, else primary."""
        if self.testing and self.database_test_url:
            return self.database_test_url
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, used as a FastAPI dependency."""
    return Settings()
