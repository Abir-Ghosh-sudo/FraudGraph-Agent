from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CaseStatus(str, Enum):
    """Lifecycle states for a fraud investigation case."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    AWAITING_EVIDENCE = "awaiting_evidence"
    AWAITING_APPROVAL = "awaiting_approval"
    ACTION_RECOMMENDED = "action_recommended"
    ACTION_EXECUTED = "action_executed"
    ESCALATED = "escalated"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class CaseTransition:
    """A recorded case status transition."""

    case_id: str
    from_status: CaseStatus | None
    to_status: CaseStatus
    reason: str
    actor: str = "agent"
    created_at: datetime = _utc_now()


class CaseLifecycle:
    """Validate and manage fraud case status transitions."""

    TRANSITIONS: dict[CaseStatus | None, set[CaseStatus]] = {
        None: {
            CaseStatus.OPEN,
        },
        CaseStatus.OPEN: {
            CaseStatus.INVESTIGATING,
            CaseStatus.CANCELLED,
        },
        CaseStatus.INVESTIGATING: {
            CaseStatus.AWAITING_EVIDENCE,
            CaseStatus.ACTION_RECOMMENDED,
            CaseStatus.ESCALATED,
            CaseStatus.CANCELLED,
        },
        CaseStatus.AWAITING_EVIDENCE: {
            CaseStatus.INVESTIGATING,
            CaseStatus.ESCALATED,
            CaseStatus.CANCELLED,
        },
        CaseStatus.ACTION_RECOMMENDED: {
            CaseStatus.AWAITING_APPROVAL,
            CaseStatus.ACTION_EXECUTED,
            CaseStatus.INVESTIGATING,
            CaseStatus.ESCALATED,
            CaseStatus.CLOSED,
        },
        CaseStatus.AWAITING_APPROVAL: {
            CaseStatus.ACTION_EXECUTED,
            CaseStatus.ACTION_RECOMMENDED,
            CaseStatus.ESCALATED,
            CaseStatus.CANCELLED,
        },
        CaseStatus.ACTION_EXECUTED: {
            CaseStatus.INVESTIGATING,
            CaseStatus.CLOSED,
            CaseStatus.ESCALATED,
        },
        CaseStatus.ESCALATED: {
            CaseStatus.INVESTIGATING,
            CaseStatus.ACTION_RECOMMENDED,
            CaseStatus.CLOSED,
            CaseStatus.CANCELLED,
        },
        CaseStatus.CLOSED: set(),
        CaseStatus.CANCELLED: set(),
    }

    TERMINAL_STATES = {
        CaseStatus.CLOSED,
        CaseStatus.CANCELLED,
    }

    def __init__(
        self,
        *,
        case_id: str,
        status: CaseStatus = CaseStatus.OPEN,
    ) -> None:
        self.case_id = case_id
        self._status = self._normalize_status(status)
        self._history: list[CaseTransition] = []

    @property
    def status(self) -> CaseStatus:
        return self._status

    @property
    def history(self) -> tuple[CaseTransition, ...]:
        return tuple(self._history)

    @property
    def is_terminal(self) -> bool:
        return self._status in self.TERMINAL_STATES

    def can_transition(
        self,
        target: CaseStatus | str,
    ) -> bool:
        target_status = self._normalize_status(target)

        return target_status in self.TRANSITIONS.get(
            self._status,
            set(),
        )

    def transition(
        self,
        target: CaseStatus | str,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseTransition:
        target_status = self._normalize_status(target)

        if not reason.strip():
            raise ValueError(
                "A reason is required for a case transition."
            )

        if not self.can_transition(target_status):
            raise ValueError(
                f"Invalid case transition: "
                f"{self._status.value} -> {target_status.value}"
            )

        transition = CaseTransition(
            case_id=self.case_id,
            from_status=self._status,
            to_status=target_status,
            reason=reason,
            actor=actor,
        )

        self._status = target_status
        self._history.append(transition)

        return transition

    def reopen(
        self,
        *,
        reason: str,
        actor: str = "agent",
    ) -> CaseTransition:
        if not self.is_terminal:
            raise ValueError(
                "Only terminal cases can be reopened."
            )

        previous = self._status

        transition = CaseTransition(
            case_id=self.case_id,
            from_status=previous,
            to_status=CaseStatus.INVESTIGATING,
            reason=reason,
            actor=actor,
        )

        self._status = CaseStatus.INVESTIGATING
        self._history.append(transition)

        return transition

    def reset_history(self) -> None:
        """Clear in-memory transition history."""
        self._history.clear()

    def export(self) -> dict[str, Any]:
        """Serialize current lifecycle state."""
        return {
            "case_id": self.case_id,
            "status": self._status.value,
            "is_terminal": self.is_terminal,
            "history": [
                {
                    "case_id": item.case_id,
                    "from_status": (
                        item.from_status.value
                        if item.from_status
                        else None
                    ),
                    "to_status": item.to_status.value,
                    "reason": item.reason,
                    "actor": item.actor,
                    "created_at": item.created_at.isoformat(),
                }
                for item in self._history
            ],
        }

    @staticmethod
    def _normalize_status(
        status: CaseStatus | str,
    ) -> CaseStatus:
        if isinstance(status, CaseStatus):
            return status

        try:
            return CaseStatus(str(status).lower())
        except ValueError as exc:
            raise ValueError(
                f"Invalid case status: {status}"
            ) from exc