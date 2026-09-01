"""Tests for application settings.

These tests are hermetic: the autouse fixture clears the DB-related env vars so
results never depend on ambient environment (locally or in CI, which sets
DATABASE_TEST_URL). Each test then supplies exactly the values it cares about.
"""

import pytest
from pydantic import ValidationError

from src.config import Settings

ENV_VARS = ("DATABASE_URL", "DATABASE_TEST_URL", "TESTING", "ENVIRONMENT")


@pytest.fixture(autouse=True)
def clear_settings_env(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_database_url_has_default():
    """A safe default keeps the app (and CI) bootable before any DB env is set."""
    settings = Settings()
    assert settings.database_url.startswith("postgresql://")


def test_testing_flag_selects_test_database():
    settings = Settings(testing=True, database_test_url="postgresql://test")
    assert settings.active_database_url == "postgresql://test"


def test_non_testing_uses_primary_database():
    settings = Settings(
        testing=False,
        database_url="postgresql://primary",
        database_test_url="postgresql://test",
    )
    assert settings.active_database_url == "postgresql://primary"


def test_testing_without_test_url_falls_back_to_primary():
    settings = Settings(testing=True, database_url="postgresql://primary")
    assert settings.active_database_url == "postgresql://primary"


def test_production_with_default_jwt_secret_is_rejected():
    """Fail fast: production must not run on the committed dev secret."""
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret_key="dev-only-insecure-secret-change-me-in-production",
        )


def test_production_with_custom_jwt_secret_is_allowed():
    settings = Settings(
        environment="production",
        jwt_secret_key="a-sufficiently-long-real-production-secret-value",
    )
    assert settings.environment == "production"


def test_dev_with_default_jwt_secret_is_allowed():
    # The default is fine in dev/test -- only production is guarded.
    assert Settings(environment="dev").environment == "dev"
