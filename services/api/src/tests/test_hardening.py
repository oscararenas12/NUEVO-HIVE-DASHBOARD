"""Edge-hardening tests: security headers, CORS, prod docs gating, rate limiting."""

from src.config import Settings
from src.main import create_app


def test_security_headers_present(client):
    resp = client.get("/ping")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"


def test_cors_preflight_allows_configured_origin(client):
    resp = client.options(
        "/ping",
        headers={
            "Origin": "http://localhost:3007",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3007"


def test_docs_enabled_in_dev():
    app = create_app(Settings(environment="dev"))
    assert app.openapi_url == "/openapi.json"


def test_docs_disabled_in_production():
    app = create_app(
        Settings(
            environment="production",
            jwt_secret_key="a-real-long-production-secret-value-here",
        )
    )
    assert app.openapi_url is None
    assert app.docs_url is None


def test_login_is_rate_limited(client):
    from src.api.limiter import limiter

    client.post(
        "/auth/register",
        json={
            "username": "rl",
            "email": "rl@example.com",
            "password": "Str0ng-Passw0rd!",
        },
    )
    limiter.enabled = True
    try:
        statuses = [
            client.post(
                "/auth/login",
                json={"email": "rl@example.com", "password": "Str0ng-Passw0rd!"},
            ).status_code
            for _ in range(6)
        ]
    finally:
        limiter.enabled = False
    assert 429 in statuses
