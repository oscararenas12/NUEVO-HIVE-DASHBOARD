"""Tests for the auth endpoints: register, login, status, refresh, logout."""

from datetime import datetime, timedelta, timezone

import jwt

from src.config import get_settings


def register_payload(**overrides):
    data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "s3cret-pass",
    }
    data.update(overrides)
    return data


# ── register ──


def test_register_returns_201_and_user_without_password(client):
    resp = client.post("/auth/register", json=register_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert body["role"] == "employee"
    assert body["is_active"] is True
    assert "id" in body
    # Secrets must never appear in the response.
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_returns_400(client):
    client.post("/auth/register", json=register_payload(username="a1", email="dup@example.com"))
    resp = client.post("/auth/register", json=register_payload(username="a2", email="dup@example.com"))
    assert resp.status_code == 400


def test_register_duplicate_username_returns_400(client):
    client.post("/auth/register", json=register_payload(username="same", email="one@example.com"))
    resp = client.post("/auth/register", json=register_payload(username="same", email="two@example.com"))
    assert resp.status_code == 400


def test_register_missing_fields_returns_422(client):
    resp = client.post("/auth/register", json={"email": "x@example.com"})
    assert resp.status_code == 422


# ── login ──


def test_login_valid_returns_token(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "s3cret-pass"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email_returns_401(client):
    resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever"})
    assert resp.status_code == 401


# ── status ──


def _register_and_token(client):
    client.post("/auth/register", json=register_payload())
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "s3cret-pass"})
    return resp.json()["access_token"]


def test_status_with_valid_token_returns_user(client):
    token = _register_and_token(client)
    resp = client.get("/auth/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "password_hash" not in body


def test_status_without_token_returns_401(client):
    resp = client.get("/auth/status")
    assert resp.status_code == 401


def test_status_with_malformed_token_returns_401(client):
    resp = client.get("/auth/status", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


# ── refresh / logout ──


def _login(client, **overrides):
    client.post("/auth/register", json=register_payload(**overrides))
    email = overrides.get("email", "alice@example.com")
    password = overrides.get("password", "s3cret-pass")
    return client.post("/auth/login", json={"email": email, "password": password})


def test_login_sets_httponly_refresh_cookie(client):
    resp = _login(client)
    assert resp.status_code == 200
    assert "refresh_token" in resp.cookies
    assert "httponly" in resp.headers.get("set-cookie", "").lower()


def test_refresh_returns_new_access_token(client):
    _login(client)  # the client cookie jar now holds the refresh cookie
    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    assert resp.json()["access_token"]
    assert resp.json()["token_type"] == "bearer"


def test_refresh_without_cookie_returns_401(client):
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_with_expired_token_returns_401(client):
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "1", "type": "refresh", "exp": datetime.now(timezone.utc) - timedelta(days=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    client.cookies.set("refresh_token", expired)
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_with_access_token_as_cookie_returns_401(client):
    access = _login(client).json()["access_token"]
    client.cookies.set("refresh_token", access)  # wrong token type
    assert client.post("/auth/refresh").status_code == 401


def test_logout_clears_cookie_and_blocks_refresh(client):
    _login(client)
    assert client.post("/auth/logout").status_code == 200
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_token_not_valid_as_bearer(client):
    refresh = _login(client).cookies.get("refresh_token")
    resp = client.get("/auth/status", headers={"Authorization": f"Bearer {refresh}"})
    assert resp.status_code == 401
