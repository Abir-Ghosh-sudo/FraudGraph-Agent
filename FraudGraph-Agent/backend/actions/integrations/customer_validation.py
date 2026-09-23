"""
Customer-validation integration boundary.

Provides a safe interface for requesting and recording customer/account-owner
validation during fraud investigations.

The default implementation is dry-run and does not contact an external
identity, authentication, or KYC provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class ValidationResult:
    """Result of a customer-validation operation."""

    customer_id: str
    validation_type: str
    status: str
    message: str
    provider_reference: str | None = None
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.executed_at is None:
            self.executed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "customer_id": self.customer_id,
            "validation_type": self.validation_type,
            "status": self.status,
            "message": self.message,
            "provider_reference": self.provider_reference,
            "executed_at": self.executed_at.isoformat(),
        }


class CustomerValidation:
    """
    Customer-validation abstraction.

    Validation is intentionally explicit and externally controlled. The
    fraud agent may request validation, but this class does not bypass
    customer authentication or identity-provider controls.
    """

    def __init__(self, *, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    @staticmethod
    def _customer_id(payload: Mapping[str, Any]) -> str:
        value = payload.get("customer_id") or payload.get("account_owner_id")

        if value is None or not str(value).strip():
            raise ValueError("customer_id is required.")

        return str(value)

    def request_owner_validation(
        self,
        payload: Mapping[str, Any],
    ) -> ValidationResult:
        """Request validation of the account owner."""
        customer_id = self._customer_id(payload)

        validation_type = str(
            payload.get("validation_type", "account_owner")
        )

        if self.dry_run:
            return ValidationResult(
                customer_id=customer_id,
                validation_type=validation_type,
                status="requested",
                message=(
                    f"Owner validation for customer '{customer_id}' "
                    "would be requested."
                ),
                provider_reference=f"SIM-VALIDATE-{customer_id}",
            )

        return ValidationResult(
            customer_id=customer_id,
            validation_type=validation_type,
            status="requested",
            message=(
                f"Owner validation for customer '{customer_id}' "
                "was requested."
            ),
        )

    def record_validation(
        self,
        payload: Mapping[str, Any],
    ) -> ValidationResult:
        """Record a validation result supplied by an authorized provider."""
        customer_id = self._customer_id(payload)

        validation_type = str(
            payload.get("validation_type", "account_owner")
        )
        validation_status = str(
            payload.get("validation_status", "unknown")
        )

        return ValidationResult(
            customer_id=customer_id,
            validation_type=validation_type,
            status=validation_status,
            message=(
                f"Validation result for customer '{customer_id}' "
                f"recorded as '{validation_status}'."
            ),
            provider_reference=(
                str(payload["provider_reference"])
                if payload.get("provider_reference") is not None
                else None
            ),
        )

    def handler(self, action: str):
        """Return an executor-compatible handler."""
        handlers = {
            "request_owner_validation": self.request_owner_validation,
            "record_validation": self.record_validation,
        }

        try:
            return handlers[action]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported customer-validation action: {action}"
            ) from exc