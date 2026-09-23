"""
Transaction-control integration boundary.

This module provides safe, dependency-free transaction action handlers.
A real banking/payment provider can later be injected behind this interface
without changing the fraud-agent orchestration layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class TransactionActionResult:
    """Result returned by a transaction-control operation."""

    transaction_id: str
    action: str
    status: str
    message: str
    provider_reference: str | None = None
    executed_at: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.executed_at is None:
            self.executed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "transaction_id": self.transaction_id,
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "provider_reference": self.provider_reference,
            "executed_at": self.executed_at.isoformat(),
        }


class TransactionControl:
    """
    Transaction-control abstraction.

    By default this implementation operates in a safe simulated mode.
    It does not contact a real financial institution.
    """

    def __init__(self, *, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    @staticmethod
    def _transaction_id(payload: Mapping[str, Any]) -> str:
        value = payload.get("transaction_id") or payload.get("id")

        if value is None or not str(value).strip():
            raise ValueError("transaction_id is required.")

        return str(value)

    def allow_transaction(
        self,
        payload: Mapping[str, Any],
    ) -> TransactionActionResult:
        """Allow a transaction to proceed."""
        transaction_id = self._transaction_id(payload)

        if self.dry_run:
            return TransactionActionResult(
                transaction_id=transaction_id,
                action="allow_transaction",
                status="simulated",
                message=(
                    f"Transaction '{transaction_id}' would be allowed "
                    "in a live transaction-control system."
                ),
                provider_reference=f"SIM-ALLOW-{transaction_id}",
            )

        return TransactionActionResult(
            transaction_id=transaction_id,
            action="allow_transaction",
            status="accepted",
            message=f"Transaction '{transaction_id}' was allowed.",
        )

    def block_transaction(
        self,
        payload: Mapping[str, Any],
    ) -> TransactionActionResult:
        """Block a transaction."""
        transaction_id = self._transaction_id(payload)

        if self.dry_run:
            return TransactionActionResult(
                transaction_id=transaction_id,
                action="block_transaction",
                status="simulated",
                message=(
                    f"Transaction '{transaction_id}' would be blocked "
                    "in a live transaction-control system."
                ),
                provider_reference=f"SIM-BLOCK-{transaction_id}",
            )

        return TransactionActionResult(
            transaction_id=transaction_id,
            action="block_transaction",
            status="accepted",
            message=f"Transaction '{transaction_id}' was blocked.",
        )

    def handler(self, action: str):
        """
        Return an executor-compatible handler for a supported action.
        """
        handlers = {
            "allow_transaction": self.allow_transaction,
            "block_transaction": self.block_transaction,
        }

        try:
            return handlers[action]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported transaction-control action: {action}"
            ) from exc