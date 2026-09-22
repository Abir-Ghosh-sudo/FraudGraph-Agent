from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import Settings, get_settings
from backend.app.dependencies import initialize_runtime


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage application startup and shutdown.

    Startup currently performs only local runtime initialization.

    Dataset loading, TigerGraph connection, model loading and agent
    initialization will be added through dedicated services later.
    """

    settings: Settings = app.state.settings

    # Create required empty runtime directories.
    initialize_runtime(settings)

    yield

    # No persistent resources need to be closed yet.
    #
    # Later this section can close:
    #   - TigerGraph connections
    #   - HTTP clients
    #   - background workers
    #   - agent resources
    #   - other shared infrastructure


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app(
    settings: Settings | None = None,
) -> FastAPI:
    """
    Create and configure the FraudGraph Agent FastAPI application.
    """

    resolved_settings = settings or get_settings()

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

    # ------------------------------------------------------------------------
    # Application state
    # ------------------------------------------------------------------------

    app.state.settings = resolved_settings

    # ------------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------------
    # Health endpoint
    # ------------------------------------------------------------------------

    @app.get(
        "/health",
        tags=["health"],
    )
    async def health() -> dict[str, object]:
        """
        Basic application health check.

        This endpoint does not claim that TigerGraph, Ollama or the
        HHGOA dataset is available. It only reports application state.
        """

        return {
            "status": "ok",
            "application": resolved_settings.app_name,
            "version": resolved_settings.app_version,
            "environment": resolved_settings.environment,
        }

    # ------------------------------------------------------------------------
    # Configuration readiness endpoint
    # ------------------------------------------------------------------------

    @app.get(
        "/health/readiness",
        tags=["health"],
    )
    async def readiness() -> dict[str, object]:
        """
        Report configuration readiness for major infrastructure.

        This is intentionally a configuration check rather than a live
        connectivity test. Actual connectivity checks will be implemented
        by their respective clients.
        """

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

    # ------------------------------------------------------------------------
    # API routers
    # ------------------------------------------------------------------------
    #
    # Routers will be registered here as they are implemented.
    #
    # Expected future structure:
    #
    #     /api/v1/investigations
    #     /api/v1/cases
    #     /api/v1/evidence
    #     /api/v1/transactions
    #     /api/v1/customers
    #     /api/v1/graph
    #     /api/v1/actions
    #     /api/v1/policies
    #     /api/v1/memory
    #     /api/v1/benchmark
    #
    # We intentionally do not import those modules yet because they do not
    # exist in the implementation sequence.

    return app


# ============================================================================
# APPLICATION INSTANCE
# ============================================================================

settings = get_settings()

app = create_app(settings)


# ============================================================================
# DEVELOPMENT ENTRY POINT
# ============================================================================

def run() -> None:
    """
    Start the application using Uvicorn.

    This function is exposed by pyproject.toml as:

        fraudgraph-api
    """

    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )


# ============================================================================
# DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    run()