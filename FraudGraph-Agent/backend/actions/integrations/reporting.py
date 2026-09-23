"""
Reporting integration boundary for fraud investigations.

Provides a safe interface for preparing regulatory/reporting actions.
Actual external submission must be performed by an authorized reporting
system and is never assumed by the fraud agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class ReportingResult:
    """Result returned by a reporting operation."""

    action: str
    status: str
    message: str
    case_id: str | None = None
    report_reference: str | None = None
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
            "report_reference": self.report_reference,
            "executed_at": self.executed_at.isoformat(),
        }


class ReportingIntegration:
    """
    Reporting-system abstraction.

    The default mode is dry-run. It prepares a reporting action without
    transmitting information to an external regulator or reporting system.
    """

    def __init__(self, *, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    @staticmethod
    def _case_id(payload: Mapping[str, Any]) -> str:
        value = payload.get("case_id")

        if value is None or not str(value).strip():
            raise ValueError("case_id is required for reporting.")

        return str(value)

    def prepare_sar(
        self,
        payload: Mapping[str, Any],
    ) -> ReportingResult:
        """Prepare a suspicious-activity report for authorized review."""
        case_id = self._case_id(payload)

        if self.dry_run:
            return ReportingResult(
                action="file_sar",
                status="prepared",
                message=(
                    f"SAR for case '{case_id}' was prepared for "
                    "authorized review; no external filing occurred."
                ),
                case_id=case_id,
                report_reference=f"SIM-SAR-{case_id}",
            )

        return ReportingResult(
            action="file_sar",
            status="prepared",
            message=(
                f"SAR for case '{case_id}' was prepared for "
                "authorized submission."
            ),
            case_id=case_id,
        )

    def file_sar(
        self,
        payload: Mapping[str, Any],
    ) -> ReportingResult:
        """
        Submit a SAR through an explicitly authorized reporting provider.

        This default implementation deliberately does not perform external
        filing.
        """
        case_id = self._case_id(payload)

        return ReportingResult(
            action="file_sar",
            status="pending_provider",
            message=(
                f"SAR for case '{case_id}' requires an authorized "
                "external reporting provider."
            ),
            case_id=case_id,
        )

    def handler(self, action: str):
        """Return an executor-compatible handler."""
        handlers = {
            "prepare_sar": self.prepare_sar,
            "file_sar": self.file_sar,
        }

        try:
            return handlers[action]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported reporting action: {action}"
            ) from exc