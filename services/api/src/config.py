"""Application settings.

Loaded from environment variables (and an optional .env file). Field names map
case-insensitively to env vars, so `database_url` reads `DATABASE_URL`, etc.
See https://fastapi.tiangolo.com/advanced/settings/
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The committed dev default; production must override JWT_SECRET_KEY (see validator).
DEV_JWT_SECRET = "dev-only-insecure-secret-change-me-in-production"


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
    jwt_secret_key: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Browser origins allowed to call the API (the SPA in dev). Env override
    # (CORS_ORIGINS) must be JSON, e.g. '["https://app.example.com"]'.
    cors_origins: list[str] = ["http://localhost:3007"]
    # Rate limiting is on by default; the test suite disables it via env.
    rate_limit_enabled: bool = True

    @model_validator(mode="after")
    def _require_real_secret_in_production(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret_key == DEV_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a real value in production "
                "(the dev default is not allowed)."
            )
        return self

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
