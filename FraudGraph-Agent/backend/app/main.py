from __future__ import annotations

import os
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from backend.app.api.v1.router import api_router
from backend.app.config import Settings, get_settings
from backend.app.dependencies import initialize_runtime
from backend.app.logging import get_logger
from backend.app.middleware.auth import (
    require_api_auth,
    validate_auth_configuration,
)
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    initialize_runtime(settings)
    _maybe_start_ingest(settings)
    _maybe_build_relational_graph(settings)
    yield


def _maybe_start_ingest(settings: Settings) -> None:
    """Load the real dataset into the case/evidence stores on boot.

    The case and evidence services are in-memory, so every restart would
    otherwise leave the API empty. This runs in a background thread because it
    streams a large CSV and must not delay server startup.
    """
    if not settings.auto_ingest:
        return

    if os.environ.get("FRAUDGRAPH_DISABLE_INGEST") == "1":
        return

    root = settings.raw_data_dir
    transactions = root / "transactions.csv"
    identity = root / "identity.csv"
    model = settings.fraud_model_path
    metadata = settings.fraud_model_metadata_path

    if not transactions.exists() or not model.exists():
        return

    def _run() -> None:
        try:
            from backend.app.dependencies import get_application_context
            from backend.app.ingest import ingest_real_dataset

            ctx = get_application_context()
            results = ingest_real_dataset(
                case_service=ctx.case_service,
                evidence_service=ctx.evidence_service,
                transactions_csv=transactions,
                identity_csv=identity,
                model_path=model,
                metadata_path=metadata,
                limit=settings.ingest_case_limit,
            )
            logger.info("startup ingest finished", cases=len(results))
        except Exception as exc:  # noqa: BLE001
            # Ingest failure must never prevent the API from serving.
            logger.warning("startup ingest failed", error=str(exc))

    threading.Thread(target=_run, name="ingest", daemon=True).start()


def _maybe_build_relational_graph(settings: Settings) -> None:
    """Derive a fraud graph from the raw ledger when TigerGraph is absent.

    Without this the graph endpoints have nothing to serve, because the
    TigerGraph client is guarded by a configuration check. The graph is built
    from real transaction/identity rows and real model output; it is never
    fabricated. Built in a thread because it streams the ledger.
    """
    transactions = settings.raw_data_dir / "transactions.csv"
    identity = settings.raw_data_dir / "identity.csv"

    if not transactions.exists():
        return

    def _run() -> None:
        try:
            from backend.app.dependencies import get_graph_service
            from backend.app.services.relational_graph import RelationalFraudGraph

            graph = RelationalFraudGraph.from_dataset(
                transactions_csv=transactions,
                identity_csv=identity,
                model_path=settings.fraud_model_path,
                metadata_path=settings.fraud_model_metadata_path,
                max_rows=settings.graph_build_row_limit,
                score_transactions=settings.graph_score_row_limit,
            )
            service = get_graph_service()
            if service is not None:
                service.relational = graph
                logger.info("relational graph attached to graph service")
        except Exception as exc:  # noqa: BLE001
            logger.warning("relational graph build failed", error=str(exc))

    threading.Thread(
        target=_run, name="relational-graph", daemon=True
    ).start()


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