"""Tests for application settings.

These tests are hermetic: the autouse fixture clears the DB-related env vars so
results never depend on ambient environment (locally or in CI, which sets
DATABASE_TEST_URL). Each test then supplies exactly the values it cares about.
"""

import pytest

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
