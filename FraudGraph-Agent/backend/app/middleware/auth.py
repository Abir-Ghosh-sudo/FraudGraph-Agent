from __future__ import annotations

from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from jwt import InvalidTokenError

_SUPPORTED_HMAC_ALGORITHMS = {"HS256", "HS384", "HS512"}


def _auth_required(settings: Any) -> bool:
    return bool(settings.auth_enabled or settings.environment in {"staging", "production"})


def validate_auth_configuration(settings: Any) -> None:
    """Reject unsafe JWT configuration whenever authentication is required."""
    if not _auth_required(settings):
        return

    algorithm = str(settings.jwt_algorithm).upper()
    if algorithm not in _SUPPORTED_HMAC_ALGORITHMS:
        raise ValueError(
            "JWT_ALGORITHM must be one of HS256, HS384, or HS512 "
            "when API authentication is enabled."
        )

    secret = str(settings.jwt_secret_key or "")
    if len(secret.encode("utf-8")) < 32:
        raise ValueError(
            "JWT_SECRET_KEY must contain at least 32 UTF-8 bytes "
            "when API authentication is enabled."
        )


async def require_api_auth(request: Request) -> dict[str, Any] | None:
    """Authenticate protected API requests using a signed bearer JWT.

    Local development and tests remain unauthenticated unless AUTH_ENABLED is
    explicitly enabled. Staging and production always require authentication.
    """
    settings = request.app.state.settings
    if not _auth_required(settings):
        return None

    validate_auth_configuration(settings)

    authorization = request.headers.get("Authorization", "")
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = jwt.decode(
            token.strip(),
            settings.jwt_secret_key,
            algorithms=[str(settings.jwt_algorithm).upper()],
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token must contain a non-empty subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    principal = {
        "sub": subject.strip(),
        "role": claims.get("role", "analyst"),
        "tenant_id": claims.get("tenant_id"),
    }
    request.state.principal = principal
    return principal