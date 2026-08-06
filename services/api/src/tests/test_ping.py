"""Tests for the /ping health check endpoint."""


def test_ping_returns_200(client):
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_reports_ok_status(client):
    response = client.get("/ping")
    assert response.json()["status"] == "ok"


def test_ping_reports_environment(client):
    """The environment comes from config -- assert it's present, not a literal.

    Pinning to "dev" would falsely fail when the same endpoint runs under a
    test or CI environment, so we only assert the field exists and is a string.
    """
    body = client.get("/ping").json()
    assert "environment" in body
    assert isinstance(body["environment"], str)
