from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from backend.app.api.v1.router import api_router
from backend.app.config import Settings, get_settings
from backend.app.dependencies import initialize_runtime
from backend.app.middleware.auth import (
    require_api_auth,
    validate_auth_configuration,
)
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    initialize_runtime(settings)
    yield


def create_app(
    settings: Settings | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    validate_auth_configuration(resolved_settings)

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        description=(
            "Agentic fraud investigation system powered by "
            "TigerGraph, GraphRAG and a local LLM."
        ),
        debug=resolved_settings.debug,
        lifespan=lifespan,
    )

    app.state.settings = resolved_settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        api_router,
        prefix=resolved_settings.api_prefix,
        dependencies=[Depends(require_api_auth)],
    )

    @app.get(
        "/health",
        tags=["health"],
    )
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "application": resolved_settings.app_name,
            "version": resolved_settings.app_version,
            "environment": resolved_settings.environment,
        }

    @app.get(
        "/health/readiness",
        tags=["health"],
    )
    async def readiness() -> dict[str, object]:
        return {
            "status": "ok",
            "tigergraph_configured": (
                resolved_settings.tigergraph_configured
            ),
            "tigergraph_mcp_configured": (
                resolved_settings.tigergraph_mcp_configured
            ),
            "llm_configured": (
                resolved_settings.llm_configured
            ),
            "embeddings_configured": (
                resolved_settings.embeddings_configured
            ),
            "vector_store_configured": (
                resolved_settings.vector_store_configured
            ),
        }

    return app


settings = get_settings()
app = create_app(settings)


def run() -> None:
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )


if __name__ == "__main__":
    run()