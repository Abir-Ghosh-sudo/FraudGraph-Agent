from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.config import Settings, get_settings
from backend.app.schemas.graph import (
    GraphQueryRequest,
    GraphQueryResult,
    InvestigationSubgraph,
)
from backend.app.services.graph import GraphService
from backend.tigergraph.client import (
    TigerGraphError,
    TigerGraphRequestError,
)
from backend.tigergraph.query_runner import (
    QueryParameterError,
    QueryRegistryError,
)

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
)


def get_graph_service(
    settings: Settings = Depends(get_settings),
) -> GraphService:
    return GraphService(settings=settings)


@router.get(
    "/health",
    response_model=dict[str, Any],
)
async def graph_health(
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    try:
        return service.health()
    except TigerGraphError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/queries",
    response_model=list[dict[str, Any]],
)
async def list_graph_queries(
    service: GraphService = Depends(get_graph_service),
) -> list[dict[str, Any]]:
    if not service.is_configured():
        return []

    try:
        return service.list_queries()
    except QueryRegistryError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get(
    "/queries/{query_name}",
    response_model=dict[str, Any],
)
async def describe_graph_query(
    query_name: str,
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph is not configured.",
        )

    try:
        return service.describe_query(query_name)
    except QueryRegistryError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/query",
    response_model=GraphQueryResult,
)
async def execute_graph_query(
    request: GraphQueryRequest,
    service: GraphService = Depends(get_graph_service),
) -> GraphQueryResult:
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph is not configured.",
        )

    try:
        return service.query(request)

    except QueryParameterError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except QueryRegistryError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except TigerGraphRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/investigation/{node_id}",
    response_model=InvestigationSubgraph,
)
async def get_investigation_subgraph(
    node_id: str,
    query_name: str = Query(
        min_length=1,
        description=(
            "Registered TigerGraph query used to collect "
            "the investigation relationships."
        ),
    ),
    depth: int = Query(
        default=2,
        ge=0,
        le=10,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    service: GraphService = Depends(get_graph_service),
) -> InvestigationSubgraph:
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph is not configured.",
        )

    try:
        return service.investigation(
            root_node_id=node_id,
            query_name=query_name,
            parameters={"node_id": node_id},
            depth=depth,
            limit=limit,
        )

    except QueryParameterError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except QueryRegistryError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except TigerGraphRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/evidence",
    response_model=dict[str, Any],
)
async def collect_graph_evidence(
    request: GraphQueryRequest,
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph is not configured.",
        )

    try:
        return service.collect_graph_evidence(
            query_name=request.query_name,
            parameters=request.parameters,
            limit=request.limit,
        )

    except QueryParameterError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except QueryRegistryError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except TigerGraphRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc