from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.dependencies import get_graph_service
from backend.app.schemas.transaction import (
    Transaction,
    TransactionSearchResult,
    TransactionSummary,
)
from backend.app.services.graph import GraphService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get(
    "/{transaction_id}",
    response_model=Transaction,
)
async def get_transaction(
    transaction_id: str,
    graph: GraphService = Depends(get_graph_service),
) -> Transaction:
    if not graph.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph database is not configured. Configure TIGERGRAPH_* settings to enable transaction lookups.",
        )

    try:
        data = graph.client.get_vertex("Transaction", transaction_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction '{transaction_id}' not found.",
            )
        attributes = data.get("attributes", {})
        return Transaction(
            transaction_id=transaction_id,
            customer_id=attributes.get("customer_id"),
            account_id=attributes.get("account_id"),
            card_id=attributes.get("card_id"),
            device_id=attributes.get("device_id"),
            merchant_id=attributes.get("merchant_id"),
            amount=float(attributes.get("amount", 0.0)) if attributes.get("amount") is not None else None,
            currency=attributes.get("currency"),
            fraud_risk_score=attributes.get("fraud_risk_score"),
            country=attributes.get("country"),
            region=attributes.get("region"),
            ip_address=attributes.get("ip_address"),
            transaction_type=attributes.get("transaction_type"),
            status=attributes.get("status"),
            attributes=attributes,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying transaction: {str(exc)}",
        )


@router.get(
    "",
    response_model=TransactionSearchResult,
)
async def search_transactions(
    customer_id: str | None = None,
    account_id: str | None = None,
    device_id: str | None = None,
    merchant_id: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    graph: GraphService = Depends(get_graph_service),
) -> TransactionSearchResult:
    if not graph.is_configured():
        # Gracefully return empty results when unconfigured
        return TransactionSearchResult(
            transactions=[],
            total=0,
            offset=offset,
            limit=limit,
        )

    try:
        vertices = graph.client.get_vertices("Transaction", limit=limit)
        summaries: list[TransactionSummary] = []
        for v in vertices:
            attrs = v.get("attributes", {})
            v_id = str(v.get("v_id", ""))
            # Apply filters if provided
            if customer_id and attrs.get("customer_id") != customer_id:
                continue
            if account_id and attrs.get("account_id") != account_id:
                continue
            if device_id and attrs.get("device_id") != device_id:
                continue
            if merchant_id and attrs.get("merchant_id") != merchant_id:
                continue

            summaries.append(
                TransactionSummary(
                    transaction_id=v_id,
                    amount=float(attrs.get("amount", 0.0)) if attrs.get("amount") is not None else None,
                    merchant_id=attrs.get("merchant_id"),
                    customer_id=attrs.get("customer_id"),
                    device_id=attrs.get("device_id"),
                    status=attrs.get("status"),
                )
            )

        return TransactionSearchResult(
            transactions=summaries[offset : offset + limit],
            total=len(summaries),
            offset=offset,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying transactions: {str(exc)}",
        )