from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import (
    ActionCandidate,
    ActionPlan,
    ActionRiskLevel,
    ActionStatus,
    ActionType,
    ApprovalRoute,
    ApprovalStatus,
    NextBestAction,
)
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus, RiskLevel
from backend.policy.engine import PolicyEngine

logger = get_logger("agent.nodes.recommend_action")


class RecommendActionNode:
    """Evaluates risk and policy to produce candidate actions and select the Next Best Action."""

    def __init__(self, settings: Settings, policy_engine: PolicyEngine | None = None) -> None:
        self.settings = settings
        self.policy_engine = policy_engine or PolicyEngine(settings=settings)

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.RECOMMEND_ACTION)

        assessment = updated.get("assessment")
        risk_level = assessment.risk_level if assessment else RiskLevel.UNKNOWN
        risk_score = assessment.risk_score if assessment and assessment.risk_score is not None else 0.5

        evidence_list = updated.get("evidence", [])
        evidence_ids = [getattr(e, "evidence_id", "") for e in evidence_list if getattr(e, "evidence_id", "")]
        patterns = updated.get("detected_patterns", [])

        candidates: list[ActionCandidate] = []

        if risk_level == RiskLevel.CRITICAL or risk_score >= 0.85:
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.BLOCK_ACCOUNT,
                    title="Block compromised account immediately",
                    rationale=f"Critical fraud risk score ({risk_score:.2f}) with {len(patterns)} confirmed fraud patterns.",
                    evidence_ids=evidence_ids[:10],
                    required_evidence=["device_match", "ip_risk"],
                    risk_level=ActionRiskLevel.CRITICAL,
                    requires_approval=True,
                    approval_route=ApprovalRoute.SENIOR_ANALYST,
                    policy_references=["POL-ACC-001: Immediate High-Risk Account Restriction"],
                    priority=0.95,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.BLOCK_TRANSACTION,
                    title="Block suspicious transaction",
                    rationale="High confidence fraud pattern detected.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.HIGH,
                    requires_approval=True,
                    approval_route=ApprovalRoute.ANALYST,
                    policy_references=["POL-TXN-002: Real-time Transaction Blocking"],
                    priority=0.90,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.FILE_REPORT,
                    title="File regulatory SAR / STR report",
                    rationale="Confirmed malicious activity warrants regulatory filing.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.HIGH,
                    requires_approval=True,
                    approval_route=ApprovalRoute.COMPLIANCE,
                    policy_references=["POL-REP-003: AML/CFT Suspicious Activity Reporting"],
                    priority=0.85,
                )
            )
        elif risk_level == RiskLevel.HIGH or risk_score >= 0.65:
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.BLOCK_TRANSACTION,
                    title="Block high-risk transaction",
                    rationale=f"Elevated risk score ({risk_score:.2f}) with observed anomalies.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.HIGH,
                    requires_approval=True,
                    approval_route=ApprovalRoute.ANALYST,
                    policy_references=["POL-TXN-002: Real-time Transaction Blocking"],
                    priority=0.85,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.REQUEST_STEP_UP_AUTHENTICATION,
                    title="Enforce step-up 2FA verification",
                    rationale="Challenging customer identity to prevent unauthorized takeover.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.MEDIUM,
                    requires_approval=False,
                    approval_route=ApprovalRoute.NONE,
                    policy_references=["POL-SEC-004: Step-Up Authentication Rules"],
                    priority=0.80,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.REQUEST_ANALYST_REVIEW,
                    title="Assign case for priority analyst review",
                    rationale="Complex risk pattern requires human analyst verification.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.MEDIUM,
                    requires_approval=False,
                    approval_route=ApprovalRoute.ANALYST,
                    policy_references=["POL-OPS-005: Escalation Protocol"],
                    priority=0.75,
                )
            )
        elif risk_level == RiskLevel.MEDIUM or risk_score >= 0.35:
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.REQUEST_CUSTOMER_VALIDATION,
                    title="Request customer transaction confirmation",
                    rationale=f"Moderate risk ({risk_score:.2f}) observed; prompt customer to confirm intent.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.LOW,
                    requires_approval=False,
                    approval_route=ApprovalRoute.NONE,
                    policy_references=["POL-SEC-004: Customer Confirmation"],
                    priority=0.65,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.MONITOR_TRANSACTION,
                    title="Add transaction and related entities to active monitoring",
                    rationale="Moderate anomalies detected without decisive fraud markers.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.LOW,
                    requires_approval=False,
                    approval_route=ApprovalRoute.NONE,
                    policy_references=["POL-MON-006: Enhanced Velocity Monitoring"],
                    priority=0.60,
                )
            )
        else:
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.ALLOW_TRANSACTION,
                    title="Allow transaction to proceed normally",
                    rationale=f"Low risk score ({risk_score:.2f}) and no active fraud patterns.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.LOW,
                    requires_approval=False,
                    approval_route=ApprovalRoute.NONE,
                    policy_references=["POL-TXN-001: Standard Transaction Clearance"],
                    priority=0.50,
                )
            )
            candidates.append(
                ActionCandidate(
                    action_type=ActionType.MONITOR_TRANSACTION,
                    title="Maintain baseline transaction logging",
                    rationale="Standard operational compliance monitoring.",
                    evidence_ids=evidence_ids[:10],
                    risk_level=ActionRiskLevel.LOW,
                    requires_approval=False,
                    approval_route=ApprovalRoute.NONE,
                    policy_references=["POL-MON-001: Routine Logging"],
                    priority=0.30,
                )
            )

        # Sort candidates by priority descending
        candidates.sort(key=lambda c: c.priority, reverse=True)
        top_candidate = candidates[0]

        action_id = f"act_{uuid4().hex[:12]}"
        now = datetime.now(UTC)

        selected_action = NextBestAction(
            action_id=action_id,
            action_type=top_candidate.action_type,
            title=top_candidate.title,
            rationale=top_candidate.rationale,
            status=ActionStatus.PENDING_APPROVAL if top_candidate.requires_approval else ActionStatus.PROPOSED,
            evidence_ids=top_candidate.evidence_ids,
            policy_references=top_candidate.policy_references,
            risk_level=top_candidate.risk_level,
            priority=top_candidate.priority,
            requires_approval=top_candidate.requires_approval,
            approval_status=ApprovalStatus.PENDING if top_candidate.requires_approval else ApprovalStatus.NOT_REQUIRED,
            approval_route=top_candidate.approval_route,
            case_id=updated.get("case_id"),
            investigation_id=updated.get("investigation_id"),
            created_at=now,
        )

        plan = ActionPlan(
            candidates=candidates,
            selected_action=selected_action,
            explanation=f"Selected '{top_candidate.title}' as the primary action based on risk level {risk_level.value}.",
            requires_human_approval=top_candidate.requires_approval,
        )

        updated["action_plan"] = plan
        updated["selected_action"] = selected_action
        updated["status"] = InvestigationStatus.ACTION_RECOMMENDED

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.ACTION_RECOMMENDED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.RECOMMEND_ACTION,
            message=f"Recommended action: {selected_action.title} (Requires Approval: {selected_action.requires_approval})",
            payload={
                "action_id": selected_action.action_id,
                "action_type": selected_action.action_type.value,
                "risk_level": selected_action.risk_level.value,
                "requires_approval": selected_action.requires_approval,
            },
            created_at=now,
        )
        updated["events"] = [*updated.get("events", []), event]

        return updated
