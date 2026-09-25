from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.errors import CaseNotFoundError, CaseStatusTransitionError
from backend.app.logging import get_logger
from backend.app.schemas.case import (
    Case,
    CaseAction,
    CaseCreate,
    CaseDecision,
    CaseFinding,
    CaseOutcome,
    CaseStatus,
    CaseUpdate,
    DecisionType,
)
from backend.app.schemas.investigation import RiskLevel

logger = get_logger(__name__)

# Valid forward transitions for case status
_VALID_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.OPEN: {
        CaseStatus.INVESTIGATING,
        CaseStatus.AWAITING_EVIDENCE,
        CaseStatus.CLOSED,
    },
    CaseStatus.INVESTIGATING: {
        CaseStatus.AWAITING_EVIDENCE,
        CaseStatus.AWAITING_APPROVAL,
        CaseStatus.ACTIONED,
        CaseStatus.ESCALATED,
        CaseStatus.RESOLVED,
        CaseStatus.CLOSED,
    },
    CaseStatus.AWAITING_EVIDENCE: {
        CaseStatus.INVESTIGATING,
        CaseStatus.ESCALATED,
        CaseStatus.CLOSED,
    },
    CaseStatus.AWAITING_APPROVAL: {
        CaseStatus.ACTIONED,
        CaseStatus.RESOLVED,
        CaseStatus.ESCALATED,
        CaseStatus.CLOSED,
    },
    CaseStatus.ACTIONED: {
        CaseStatus.RESOLVED,
        CaseStatus.ESCALATED,
        CaseStatus.CLOSED,
    },
    CaseStatus.ESCALATED: {
        CaseStatus.RESOLVED,
        CaseStatus.CLOSED,
    },
    CaseStatus.RESOLVED: {
        CaseStatus.CLOSED,
    },
    CaseStatus.CLOSED: set(),
}


class CaseService:
    """
    In-memory case management service.

    Manages case lifecycle with validated status transitions.
    All write operations update `updated_at`.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cases: dict[str, Case] = {}

    def create(self, payload: CaseCreate) -> Case:
        now = datetime.now(UTC)
        case_id = f"case_{uuid4().hex}"

        case = Case(
            case_id=case_id,
            investigation_id=payload.investigation_id,
            transaction_id=payload.transaction_id,
            customer_id=payload.customer_id,
            account_id=payload.account_id,
            title=payload.title,
            description=payload.description,
            status=CaseStatus.OPEN,
            created_at=now,
            updated_at=now,
        )

        self._cases[case_id] = case

        logger.info(
            "case created",
            case_id=case_id,
            investigation_id=payload.investigation_id,
        )

        return case

    def get(self, case_id: str) -> Case:
        case = self._cases.get(case_id)
        if case is None:
            raise CaseNotFoundError(f"Case '{case_id}' not found.")
        return case

    def list(
        self,
        *,
        investigation_id: str | None = None,
        status: CaseStatus | None = None,
        risk_level: RiskLevel | None = None,
    ) -> list[Case]:
        cases = list(self._cases.values())

        if investigation_id:
            cases = [c for c in cases if c.investigation_id == investigation_id]

        if status:
            cases = [c for c in cases if c.status == status]

        if risk_level:
            cases = [c for c in cases if c.risk_level == risk_level]

        return sorted(cases, key=lambda c: c.created_at, reverse=True)

    def update(self, case_id: str, payload: CaseUpdate) -> Case:
        case = self.get(case_id)
        now = datetime.now(UTC)

        if payload.status is not None:
            self._validate_transition(case.status, payload.status)
            case.status = payload.status
            if payload.status == CaseStatus.RESOLVED:
                case.resolved_at = now
            if payload.status == CaseStatus.CLOSED:
                case.closed_at = now

        if payload.risk_score is not None:
            case.risk_score = payload.risk_score

        if payload.risk_level is not None:
            case.risk_level = payload.risk_level

        if payload.outcome is not None:
            case.outcome = payload.outcome

        if payload.title is not None:
            case.title = payload.title

        if payload.description is not None:
            case.description = payload.description

        case.updated_at = now
        return case

    def add_finding(
        self,
        case_id: str,
        *,
        title: str,
        description: str,
        evidence_ids: list[str] | None = None,
        confidence: float | None = None,
    ) -> CaseFinding:
        case = self.get(case_id)
        now = datetime.now(UTC)

        finding = CaseFinding(
            finding_id=f"finding_{uuid4().hex[:8]}",
            title=title,
            description=description,
            evidence_ids=evidence_ids or [],
            confidence=confidence,
            created_at=now,
        )

        case.findings.append(finding)
        case.updated_at = now

        return finding

    def add_decision(
        self,
        case_id: str,
        *,
        decision_type: DecisionType,
        rationale: str,
        evidence_ids: list[str] | None = None,
        requires_approval: bool = False,
        approved_by: str | None = None,
    ) -> CaseDecision:
        case = self.get(case_id)
        now = datetime.now(UTC)

        decision = CaseDecision(
            decision_id=f"dec_{uuid4().hex[:8]}",
            decision_type=decision_type,
            rationale=rationale,
            evidence_ids=evidence_ids or [],
            requires_approval=requires_approval,
            approved_by=approved_by,
            created_at=now,
        )

        case.decisions.append(decision)
        case.updated_at = now

        return decision

    def add_action(
        self,
        case_id: str,
        *,
        action_type: str,
        status: str = "proposed",
        rationale: str | None = None,
        requires_approval: bool = False,
        approval_id: str | None = None,
        result: dict[str, Any] | None = None,
    ) -> CaseAction:
        case = self.get(case_id)
        now = datetime.now(UTC)

        action = CaseAction(
            action_id=f"act_{uuid4().hex[:8]}",
            action_type=action_type,
            status=status,
            rationale=rationale,
            requires_approval=requires_approval,
            approval_id=approval_id,
            result=result or {},
            created_at=now,
        )

        case.actions.append(action)
        case.updated_at = now

        return action

    def set_outcome(
        self,
        case_id: str,
        *,
        outcome: CaseOutcome,
        risk_score: float | None = None,
        risk_level: RiskLevel | None = None,
        fraud_type: str | None = None,
    ) -> Case:
        case = self.get(case_id)
        now = datetime.now(UTC)

        case.outcome = outcome
        if risk_score is not None:
            case.risk_score = risk_score
        if risk_level is not None:
            case.risk_level = risk_level
        if fraud_type is not None:
            case.fraud_type = fraud_type
        case.updated_at = now

        return case

    def add_evidence_id(self, case_id: str, evidence_id: str) -> Case:
        case = self.get(case_id)
        if evidence_id not in case.evidence_ids:
            case.evidence_ids.append(evidence_id)
            case.updated_at = datetime.now(UTC)
        return case

    @staticmethod
    def _validate_transition(
        current: CaseStatus,
        target: CaseStatus,
    ) -> None:
        allowed = _VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise CaseStatusTransitionError(
                f"Cannot transition case from '{current}' to '{target}'.",
                detail={
                    "current": current,
                    "target": target,
                    "allowed": sorted(s.value for s in allowed),
                },
            )
