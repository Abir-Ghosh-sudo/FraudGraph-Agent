"""
CRM integration boundary for fraud-investigation case actions.

Provides dependency-free handlers for creating and updating investigation
cases. A real CRM/case-management provider can later be injected behind
this interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class CRMActionResult:
    """Result returned by a CRM operation."""

    action: str
    status: str
    message: str
    case_id: str | None = None
    provider_reference: str | None = None
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.executed_at is None:
            self.executed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "case_id": self.case_id,
            "provider_reference": self.provider_reference,
            "executed_at": self.executed_at.isoformat(),
        }


class CRMIntegration:
    """
    Case-management integration abstraction.

    The default implementation is dry-run and does not contact an external
    CRM system.
    """

    def __init__(self, *, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    @staticmethod
    def _case_id(payload: Mapping[str, Any]) -> str | None:
        value = payload.get("case_id") or payload.get("id")

        if value is None:
            return None

        value = str(value).strip()
        return value or None

    def create_case(
        self,
        payload: Mapping[str, Any],
    ) -> CRMActionResult:
        """Create a fraud investigation case."""
        supplied_case_id = self._case_id(payload)

        case_id = supplied_case_id or (
            f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        )

        if self.dry_run:
            return CRMActionResult(
                action="create_case",
                status="simulated",
                message=f"Case '{case_id}' would be created.",
                case_id=case_id,
                provider_reference=f"SIM-CASE-{case_id}",
            )

        return CRMActionResult(
            action="create_case",
            status="accepted",
            message=f"Case '{case_id}' was created.",
            case_id=case_id,
        )

    def update_case(
        self,
        payload: Mapping[str, Any],
    ) -> CRMActionResult:
        """Update an existing fraud investigation case."""
        case_id = self._case_id(payload)

        if case_id is None:
            raise ValueError("case_id is required to update a case.")

        if self.dry_run:
            return CRMActionResult(
                action="update_case",
                status="simulated",
                message=f"Case '{case_id}' would be updated.",
                case_id=case_id,
                provider_reference=f"SIM-UPDATE-{case_id}",
            )

        return CRMActionResult(
            action="update_case",
            status="accepted",
            message=f"Case '{case_id}' was updated.",
            case_id=case_id,
        )

    def handler(self, action: str):
        """Return an executor-compatible handler."""
        handlers = {
            "create_case": self.create_case,
            "update_case": self.update_case,
        }

        try:
            return handlers[action]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported CRM action: {action}"
            ) from exc