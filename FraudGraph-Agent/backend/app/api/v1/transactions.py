from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.transaction import (
    Transaction,
    TransactionSearchResult,
)


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
) -> Transaction:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transaction data service is not configured yet.",
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
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
) -> TransactionSearchResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transaction data service is not configured yet.",
    )