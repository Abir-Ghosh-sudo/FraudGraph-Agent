from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.customer import (
    Customer,
    CustomerSearchResult,
)


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
) -> Customer:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Customer data service is not configured yet.",
    )


@router.get(
    "",
    response_model=CustomerSearchResult,
)
async def search_customers(
    status: str | None = None,
    country: str | None = None,
    region: str | None = None,
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
) -> CustomerSearchResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Customer data service is not configured yet.",
    )