"""Shared pytest fixtures for the API test suite."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """A FastAPI TestClient wrapping the app."""
    return TestClient(app)
