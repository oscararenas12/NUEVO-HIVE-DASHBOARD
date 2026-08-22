"""Tests for the auth endpoints: register, login, status."""


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
