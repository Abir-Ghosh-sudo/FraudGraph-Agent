from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.graph import (
    GraphQueryRequest,
    GraphQueryResult,
    InvestigationSubgraph,
)


router = APIRouter(
    prefix="/graph",
    tags=["graph"],
)


@router.post(
    "/query",
    response_model=GraphQueryResult,
)
async def execute_graph_query(
    payload: GraphQueryRequest,
) -> GraphQueryResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Graph query service is not configured yet.",
    )


@router.get(
    "/investigation/{node_id}",
    response_model=InvestigationSubgraph,
)
async def get_investigation_subgraph(
    node_id: str,
    depth: int = 2,
) -> InvestigationSubgraph:
    if depth < 0 or depth > 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Graph depth must be between 0 and 10.",
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Graph service is not configured yet.",
    )