"""Shared pytest fixtures for the API test suite.

Tests run against a real PostgreSQL database (see DATABASE_TEST_URL). Each test
runs inside a transaction that is rolled back on teardown, so tests stay isolated
and the database is left pristine -- even though the code under test commits.
This is the SQLAlchemy "join an external transaction" recipe with a restarting
SAVEPOINT.
"""

import os

# Disable rate limiting for the suite BEFORE importing the app -- the limiter reads
# this at import time. Individual tests re-enable it directly (see test_hardening.py).
os.environ["RATE_LIMIT_ENABLED"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from src.db import get_session
from src.main import app

# Import models so SQLModel.metadata is aware of every table before create_all.
from src.api.users import models  # noqa: F401

# CI sets DATABASE_TEST_URL to its Postgres service. Locally, point at the
# api-db container's exposed port (see DEVLOG for the one-time hive_test setup).
TEST_DATABASE_URL = os.getenv(
    "DATABASE_TEST_URL",
    "postgresql://postgres:postgres@localhost:5436/hive_test",
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session(engine):
    """A Session bound to a transaction that is rolled back after each test.

    A SAVEPOINT is (re)opened so commits inside the code under test are undone
    at teardown rather than persisted.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(db, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(session):
    """TestClient with get_session overridden to use the rollback session."""

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
