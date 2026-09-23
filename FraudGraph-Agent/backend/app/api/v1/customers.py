from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.dependencies import get_graph_service
from backend.app.schemas.customer import (
    Customer,
    CustomerSearchResult,
    CustomerSummary,
)
from backend.app.services.graph import GraphService

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.get(
    "/{customer_id}",
    response_model=Customer,
)
async def get_customer(
    customer_id: str,
    graph: GraphService = Depends(get_graph_service),
) -> Customer:
    if not graph.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TigerGraph database is not configured. Configure TIGERGRAPH_* settings to enable customer lookups.",
        )

    try:
        data = graph.client.get_vertex("Customer", customer_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer '{customer_id}' not found.",
            )
        attrs = data.get("attributes", {})
        return Customer(
            customer_id=customer_id,
            account_ids=attrs.get("account_ids", []),
            card_ids=attrs.get("card_ids", []),
            device_ids=attrs.get("device_ids", []),
            email_ids=attrs.get("email_ids", []),
            phone_ids=attrs.get("phone_ids", []),
            address_ids=attrs.get("address_ids", []),
            country=attrs.get("country"),
            region=attrs.get("region"),
            customer_type=attrs.get("customer_type"),
            status=attrs.get("status"),
            risk_score=attrs.get("risk_score"),
            attributes=attrs,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying customer: {str(exc)}",
        )


@router.get(
    "",
    response_model=CustomerSearchResult,
)
async def search_customers(
    status: str | None = None,
    country: str | None = None,
    region: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    graph: GraphService = Depends(get_graph_service),
) -> CustomerSearchResult:
    if not graph.is_configured():
        return CustomerSearchResult(
            customers=[],
            total=0,
            offset=offset,
            limit=limit,
        )

    try:
        vertices = graph.client.get_vertices("Customer", limit=limit)
        summaries: list[CustomerSummary] = []
        for v in vertices:
            attrs = v.get("attributes", {})
            v_id = str(v.get("v_id", ""))
            if status and attrs.get("status") != status:
                continue
            if country and attrs.get("country") != country:
                continue
            if region and attrs.get("region") != region:
                continue

            summaries.append(
                CustomerSummary(
                    customer_id=v_id,
                    account_count=len(attrs.get("account_ids", [])),
                    card_count=len(attrs.get("card_ids", [])),
                    device_count=len(attrs.get("device_ids", [])),
                    risk_score=attrs.get("risk_score"),
                    status=attrs.get("status"),
                )
            )

        return CustomerSearchResult(
            customers=summaries[offset : offset + limit],
            total=len(summaries),
            offset=offset,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying customers: {str(exc)}",
        )