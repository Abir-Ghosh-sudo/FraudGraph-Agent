from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import jwt
import pytest
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.middleware.auth import require_api_auth, validate_auth_configuration
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request


def test_development_auth_is_optional_by_default() -> None:
    settings = Settings(environment="development", auth_enabled=False)
    validate_auth_configuration(settings)


def test_production_requires_a_strong_jwt_secret() -> None:
    settings = Settings(environment="production", jwt_secret_key="too-short")

    with pytest.raises(ValueError, match="at least 32"):
        validate_auth_configuration(settings)


def test_staging_requires_a_strong_jwt_secret() -> None:
    settings = Settings(environment="staging", jwt_secret_key="too-short")

    with pytest.raises(ValueError, match="at least 32"):
        validate_auth_configuration(settings)


def test_auth_enabled_requires_a_supported_algorithm() -> None:
    settings = Settings(
        environment="testing",
        auth_enabled=True,
        jwt_secret_key="x" * 40,
        jwt_algorithm="none",
    )

    with pytest.raises(ValueError, match="HS256"):
        validate_auth_configuration(settings)


def test_auth_enabled_accepts_a_long_secret_and_hmac_algorithm() -> None:
    settings = Settings(
        environment="testing",
        auth_enabled=True,
        jwt_secret_key="x" * 40,
        jwt_algorithm="HS256",
    )
    validate_auth_configuration(settings)


def make_request(settings: Settings, authorization: str = "") -> Request:
    scope: dict[str, Any] = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/v1/",
        "raw_path": b"/api/v1/",
        "query_string": b"",
        "headers": [(b"authorization", authorization.encode("latin-1"))] if authorization else [],
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "app": SimpleNamespace(state=SimpleNamespace(settings=settings)),
    }
    return Request(scope)


def make_token(secret: str, **claims: Any) -> str:
    payload = {
        "sub": "analyst-1",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
        **claims,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def test_valid_bearer_token_sets_the_principal() -> None:
    secret = "x" * 40
    settings = Settings(
        environment="production",
        auth_enabled=False,
        jwt_secret_key=secret,
    )
    request = make_request(settings, f"Bearer {make_token(secret, role='analyst')}")

    principal = asyncio.run(require_api_auth(request))

    assert principal == {"sub": "analyst-1", "role": "analyst", "tenant_id": None}
    assert request.state.principal == principal


def test_missing_bearer_token_is_rejected_in_production() -> None:
    settings = Settings(environment="production", jwt_secret_key="x" * 40)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_api_auth(make_request(settings)))

    assert exc_info.value.status_code == 401


def test_invalid_bearer_token_is_rejected() -> None:
    settings = Settings(environment="production", jwt_secret_key="x" * 40)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_api_auth(make_request(settings, "Bearer not-a-jwt")))

    assert exc_info.value.status_code == 401


def test_production_app_protects_api_but_keeps_health_public() -> None:
    settings = Settings(
        environment="production",
        auth_enabled=False,
        jwt_secret_key="x" * 40,
    )
    client = TestClient(create_app(settings))

    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/").status_code == 401

    token = make_token(settings.jwt_secret_key, role="analyst")
    response = client.get(
        "/api/v1/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200