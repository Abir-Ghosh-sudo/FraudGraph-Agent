from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ActionRiskLevel, ActionType, ApprovalRoute
from backend.graphrag.retriever import GraphRAGRetriever, RetrievedChunk

logger = get_logger(__name__)


@dataclass
class PolicyEvaluationResult:
    allowed: bool
    requires_approval: bool
    approval_route: ApprovalRoute
    policy_references: list[str]
    restrictions: list[str]
    rationale: str
    source: str  # "document" | "default_rules"


_ACTION_RISK_MAP: dict[str, ActionRiskLevel] = {
    ActionType.ALLOW_TRANSACTION: ActionRiskLevel.LOW,
    ActionType.MONITOR_TRANSACTION: ActionRiskLevel.LOW,
    ActionType.MONITOR_ACCOUNT: ActionRiskLevel.LOW,
    ActionType.WARN_CUSTOMER: ActionRiskLevel.MEDIUM,
    ActionType.REQUEST_CUSTOMER_VALIDATION: ActionRiskLevel.MEDIUM,
    ActionType.REQUEST_STEP_UP_AUTHENTICATION: ActionRiskLevel.MEDIUM,
    ActionType.REQUEST_ANALYST_REVIEW: ActionRiskLevel.MEDIUM,
    ActionType.REQUEST_ADDITIONAL_EVIDENCE: ActionRiskLevel.LOW,
    ActionType.BLOCK_TRANSACTION: ActionRiskLevel.HIGH,
    ActionType.BLOCK_ACCOUNT: ActionRiskLevel.HIGH,
    ActionType.CREATE_CASE: ActionRiskLevel.LOW,
    ActionType.FILE_REPORT: ActionRiskLevel.HIGH,
    ActionType.CLOSE_CASE: ActionRiskLevel.MEDIUM,
}

_APPROVAL_ROUTE_MAP: dict[ActionRiskLevel, ApprovalRoute] = {
    ActionRiskLevel.LOW: ApprovalRoute.NONE,
    ActionRiskLevel.MEDIUM: ApprovalRoute.ANALYST,
    ActionRiskLevel.HIGH: ApprovalRoute.SENIOR_ANALYST,
    ActionRiskLevel.CRITICAL: ApprovalRoute.COMPLIANCE,
}

_RISK_SCORE_THRESHOLDS: dict[str, float] = {
    "low": 0.30,
    "medium": 0.60,
    "high": 0.85,
}


class PolicyEngine:
    """
    Evaluates proposed actions against loaded policy documents and configurable
    risk thresholds.

    When no policy documents are loaded, conservative built-in default rules apply.
    """

    def __init__(
        self,
        settings: Settings,
        retriever: GraphRAGRetriever | None = None,
    ) -> None:
        self.settings = settings
        self.retriever = retriever or GraphRAGRetriever(settings)
        self._initialized = False

    def initialize(self) -> None:
        if not self._initialized:
            self.retriever.initialize()
            self._initialized = True

    def evaluate_action(
        self,
        action_type: str,
        *,
        risk_score: float | None = None,
        risk_level: str | None = None,
        evidence_ids: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> PolicyEvaluationResult:
        if not self._initialized:
            self.initialize()

        evidence_ids = evidence_ids or []
        context = context or {}

        action_risk = _ACTION_RISK_MAP.get(action_type, ActionRiskLevel.MEDIUM)

        if risk_score is not None:
            action_risk = self._escalate_action_risk(action_risk, risk_score)

        policy_refs: list[str] = []
        restrictions: list[str] = []
        source = "default_rules"

        if self.settings.graphrag_enabled:
            query = f"{action_type} fraud investigation policy approval"
            if risk_level:
                query += f" {risk_level} risk"
            chunks = self.retriever.retrieve(query, top_k=3)
            if chunks:
                policy_refs = self._extract_policy_refs(chunks)
                restrictions = self._extract_restrictions(chunks, action_type)
                source = "document"

        requires_approval = self._requires_approval(action_risk, action_type)
        approval_route = _APPROVAL_ROUTE_MAP.get(action_risk, ApprovalRoute.ANALYST)
        if not requires_approval:
            approval_route = ApprovalRoute.NONE

        rationale = self._build_rationale(
            action_type=action_type,
            action_risk=action_risk,
            requires_approval=requires_approval,
            approval_route=approval_route,
            source=source,
            risk_score=risk_score,
        )

        return PolicyEvaluationResult(
            allowed=True,
            requires_approval=requires_approval,
            approval_route=approval_route,
            policy_references=policy_refs,
            restrictions=restrictions,
            rationale=rationale,
            source=source,
        )

    def get_relevant_policies(
        self,
        query: str,
        *,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if not self._initialized:
            self.initialize()
        if not self.settings.graphrag_enabled:
            return []
        k = top_k or self.settings.graphrag_top_k
        chunks = self.retriever.retrieve(query, top_k=k)
        return [
            {
                "chunk_id": c.chunk_id,
                "source_file": c.source_file,
                "page": c.page,
                "text": c.text[:500],
                "score": c.score,
            }
            for c in chunks
        ]

    def _escalate_action_risk(
        self,
        action_risk: ActionRiskLevel,
        risk_score: float,
    ) -> ActionRiskLevel:
        if risk_score >= _RISK_SCORE_THRESHOLDS["high"]:
            if action_risk == ActionRiskLevel.LOW:
                return ActionRiskLevel.MEDIUM
            if action_risk == ActionRiskLevel.MEDIUM:
                return ActionRiskLevel.HIGH
        elif risk_score >= _RISK_SCORE_THRESHOLDS["medium"]:
            if action_risk == ActionRiskLevel.LOW:
                return ActionRiskLevel.MEDIUM
        return action_risk

    def _requires_approval(
        self,
        action_risk: ActionRiskLevel,
        action_type: str,
    ) -> bool:
        if not self.settings.agent_enable_human_approval:
            return False
        if not self.settings.require_approval_for_external_actions:
            return False
        return action_risk in (
            ActionRiskLevel.MEDIUM,
            ActionRiskLevel.HIGH,
            ActionRiskLevel.CRITICAL,
        )

    @staticmethod
    def _extract_policy_refs(chunks: list[RetrievedChunk]) -> list[str]:
        return [
            f"{c.source_file.split('/')[-1].split(chr(92))[-1]}:p{c.page + 1}"
            for c in chunks
        ]

    @staticmethod
    def _extract_restrictions(
        chunks: list[RetrievedChunk],
        action_type: str,
    ) -> list[str]:
        restrictions: list[str] = []
        keywords = ["must", "required", "mandatory", "shall", "prohibited", "not permitted"]
        for chunk in chunks:
            for sentence in chunk.text.split("."):
                if any(kw in sentence.lower() for kw in keywords):
                    clean = sentence.strip()
                    if clean and len(clean) < 200:
                        restrictions.append(clean)
                        if len(restrictions) >= 3:
                            return restrictions
        return restrictions

    @staticmethod
    def _build_rationale(
        *,
        action_type: str,
        action_risk: ActionRiskLevel,
        requires_approval: bool,
        approval_route: ApprovalRoute,
        source: str,
        risk_score: float | None,
    ) -> str:
        parts = [f"Action '{action_type}' classified as {action_risk} risk."]
        if risk_score is not None:
            parts.append(f"Investigation risk score: {risk_score:.3f}.")
        if requires_approval:
            parts.append(f"Approval required via {approval_route} route.")
        else:
            parts.append("No approval required.")
        if source == "document":
            parts.append("Policy references retrieved from loaded documents.")
        else:
            parts.append("Default conservative rules applied (no policy documents loaded).")
        return " ".join(parts)
