from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str

    customer_id: str | None = None

    account_id: str | None = None

    card_id: str | None = None

    device_id: str | None = None

    merchant_id: str | None = None

    transaction_timestamp: datetime | None = None

    amount: float | None = Field(
        default=None,
        ge=0.0,
    )

    currency: str | None = None

    fraud_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    country: str | None = None

    region: str | None = None

    ip_address: str | None = None

    transaction_type: str | None = None

    status: str | None = None

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime | None = None

    updated_at: datetime | None = None


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str

    customer_id: str | None = None

    account_id: str | None = None

    card_id: str | None = None

    device_id: str | None = None

    merchant_id: str | None = None

    transaction_timestamp: datetime | None = None

    amount: float | None = Field(
        default=None,
        ge=0.0,
    )

    currency: str | None = None

    fraud_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    country: str | None = None

    region: str | None = None

    ip_address: str | None = None

    transaction_type: str | None = None

    status: str | None = None

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )


class TransactionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str

    amount: float | None = None

    transaction_timestamp: datetime | None = None

    fraud_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    merchant_id: str | None = None

    customer_id: str | None = None

    device_id: str | None = None

    status: str | None = None


class TransactionSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transactions: list[TransactionSummary] = Field(
        default_factory=list,
    )

    total: int = Field(
        default=0,
        ge=0,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=500,
    )