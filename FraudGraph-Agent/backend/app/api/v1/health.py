"""Health and readiness endpoints for the FraudGraph API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


def _utc_now() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


@router.get("")
async def health_check() -> dict[str, Any]:
    """
    Return the basic API health status.

    This endpoint intentionally performs no external dependency checks,
    so it remains useful even when TigerGraph or another downstream
    service is unavailable.
    """
    return {
        "status": "ok",
        "service": "fraudgraph-agent",
        "timestamp": _utc_now(),
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Return application readiness status.

    Dependency-specific readiness checks can be added later without
    changing the public health endpoint contract.
    """
    return {
        "status": "ready",
        "service": "fraudgraph-agent",
        "timestamp": _utc_now(),
    }