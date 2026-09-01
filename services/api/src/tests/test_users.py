"""Tests for user-management endpoints: list, get, update, deactivate.

All /users endpoints are admin-only (SEC-006); employees use GET /auth/status
for their own data.
"""

from src.api.security import hash_password
from src.api.users.models import User

EMP_PASSWORD = "employeePass1"
ADMIN_PASSWORD = "adminPass1234"


def _register_employee(client, username="emp", email="emp@example.com", password=EMP_PASSWORD):
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _make_admin(client, session, username="boss", email="boss@example.com", password=ADMIN_PASSWORD):
    """Insert an admin directly (register only creates employees), then log in."""
    session.add(
        User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
    )
    session.commit()
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ── GET /users (admin only) ──


def test_list_users_requires_auth(client):
    assert client.get("/users").status_code == 401


def test_list_users_as_admin_returns_list(client, session):
    admin_token = _make_admin(client, session)
    resp = client.get("/users", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_list_users_as_employee_returns_403(client):
    emp_token = _register_employee(client)
    assert client.get("/users", headers=_auth(emp_token)).status_code == 403


# ── GET /users/{id} (admin only) ──


def test_get_user_by_id_as_admin(client, session):
    admin_token = _make_admin(client, session)
    me = client.get("/auth/status", headers=_auth(admin_token)).json()
    resp = client.get(f"/users/{me['id']}", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == me["id"]


def test_get_user_as_employee_returns_403(client):
    emp_token = _register_employee(client)
    me = client.get("/auth/status", headers=_auth(emp_token)).json()
    assert client.get(f"/users/{me['id']}", headers=_auth(emp_token)).status_code == 403


def test_get_user_unknown_id_returns_404(client, session):
    admin_token = _make_admin(client, session)
    assert client.get("/users/999999", headers=_auth(admin_token)).status_code == 404


def test_get_user_without_token_returns_401(client):
    assert client.get("/users/1").status_code == 401


# ── PUT /users/{id} (admin only) ──


def test_admin_can_update_user(client, session):
    admin_token = _make_admin(client, session)
    emp_token = _register_employee(client)
    emp = client.get("/auth/status", headers=_auth(emp_token)).json()
    resp = client.put(
        f"/users/{emp['id']}",
        headers=_auth(admin_token),
        json={"role": "admin"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_non_admin_cannot_update_user_returns_403(client):
    emp_token = _register_employee(client)
    emp = client.get("/auth/status", headers=_auth(emp_token)).json()
    resp = client.put(
        f"/users/{emp['id']}", headers=_auth(emp_token), json={"username": "new"}
    )
    assert resp.status_code == 403


def test_update_without_token_returns_401(client):
    assert client.put("/users/1", json={"username": "x"}).status_code == 401


def test_update_unknown_user_returns_404(client, session):
    admin_token = _make_admin(client, session)
    resp = client.put("/users/999999", headers=_auth(admin_token), json={"username": "x"})
    assert resp.status_code == 404


# ── DELETE /users/{id} (admin only) ──


def test_admin_can_deactivate_user(client, session):
    admin_token = _make_admin(client, session)
    emp_token = _register_employee(client)
    emp = client.get("/auth/status", headers=_auth(emp_token)).json()
    resp = client.delete(f"/users/{emp['id']}", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_non_admin_cannot_deactivate_returns_403(client):
    emp_token = _register_employee(client)
    emp = client.get("/auth/status", headers=_auth(emp_token)).json()
    resp = client.delete(f"/users/{emp['id']}", headers=_auth(emp_token))
    assert resp.status_code == 403


def test_admin_cannot_deactivate_self_returns_400(client, session):
    admin_token = _make_admin(client, session)
    me = client.get("/auth/status", headers=_auth(admin_token)).json()
    resp = client.delete(f"/users/{me['id']}", headers=_auth(admin_token))
    assert resp.status_code == 400


def test_deactivated_user_cannot_login(client, session):
    admin_token = _make_admin(client, session)
    emp_token = _register_employee(client, email="gone@example.com", username="gone")
    emp = client.get("/auth/status", headers=_auth(emp_token)).json()
    client.delete(f"/users/{emp['id']}", headers=_auth(admin_token))
    resp = client.post("/auth/login", json={"email": "gone@example.com", "password": EMP_PASSWORD})
    assert resp.status_code == 401
