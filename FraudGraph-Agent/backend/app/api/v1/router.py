from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1 import (
    actions,
    benchmark,
    cases,
    customers,
    evidence,
    graph,
    investigations,
    memory,
    policies,
    transactions,
)


api_router = APIRouter()


api_router.include_router(
    investigations.router,
)

api_router.include_router(
    cases.router,
)

api_router.include_router(
    evidence.router,
)

api_router.include_router(
    transactions.router,
)

api_router.include_router(
    customers.router,
)

api_router.include_router(
    graph.router,
)

api_router.include_router(
    actions.router,
)

api_router.include_router(
    policies.router,
)

api_router.include_router(
    memory.router,
)

api_router.include_router(
    benchmark.router,
)


@api_router.get(
    "/",
    tags=["api"],
)
async def api_root() -> dict[str, str]:
    return {
        "name": "FraudGraph Agent API",
        "version": "v1",
        "status": "available",
    }