from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str

    account_ids: list[str] = Field(
        default_factory=list,
    )

    card_ids: list[str] = Field(
        default_factory=list,
    )

    device_ids: list[str] = Field(
        default_factory=list,
    )

    email_ids: list[str] = Field(
        default_factory=list,
    )

    phone_ids: list[str] = Field(
        default_factory=list,
    )

    address_ids: list[str] = Field(
        default_factory=list,
    )

    country: str | None = None

    region: str | None = None

    customer_type: str | None = None

    status: str | None = None

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime | None = None

    updated_at: datetime | None = None


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str

    account_ids: list[str] = Field(
        default_factory=list,
    )

    card_ids: list[str] = Field(
        default_factory=list,
    )

    device_ids: list[str] = Field(
        default_factory=list,
    )

    email_ids: list[str] = Field(
        default_factory=list,
    )

    phone_ids: list[str] = Field(
        default_factory=list,
    )

    address_ids: list[str] = Field(
        default_factory=list,
    )

    country: str | None = None

    region: str | None = None

    customer_type: str | None = None

    status: str | None = None

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    attributes: dict[str, Any] = Field(
        default_factory=dict,
    )


class CustomerSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str

    account_count: int = Field(
        default=0,
        ge=0,
    )

    card_count: int = Field(
        default=0,
        ge=0,
    )

    device_count: int = Field(
        default=0,
        ge=0,
    )

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    status: str | None = None


class CustomerSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customers: list[CustomerSummary] = Field(
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