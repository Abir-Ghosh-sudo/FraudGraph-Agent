from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state, is_step_limit_reached
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationAssessment

logger = get_logger("agent.nodes.assess_uncertainty")


class AssessUncertaintyNode:
    """Evaluates missing evidence sources, conflicting indicators, and confidence gaps to score uncertainty."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.ASSESS_UNCERTAINTY)

        assessment = updated.get("assessment")
        if assessment is None:
            assessment = InvestigationAssessment()

        evidence_list = updated.get("evidence", [])
        patterns = updated.get("detected_patterns", [])

        # 1. Missing evidence sources
        source_types = {getattr(e, "source_type", "") for e in evidence_list}
        expected_sources = {"device", "ip", "customer", "transaction"}
        missing_sources = expected_sources - source_types
        missing_penalty = len(missing_sources) * 0.15

        # 2. Evidence quantity and confidence
        if not evidence_list:
            evidence_uncertainty = 0.8
        else:
            avg_confidence = sum(getattr(e, "confidence", 0.5) for e in evidence_list) / len(evidence_list)
            evidence_uncertainty = max(0.0, (1.0 - avg_confidence) * 0.5)

        # 3. Conflicting evidence
        conflicting_penalty = 0.0
        if evidence_list:
            contradicting_count = sum(1 for e in evidence_list if getattr(e, "contradicts_prior", False))
            if contradicting_count > 0:
                conflicting_penalty = min(0.35, contradicting_count * 0.15)

        # Calculate final uncertainty score [0.0, 1.0]
        calculated_uncertainty = min(
            1.0,
            max(0.05, (missing_penalty * 0.4) + (evidence_uncertainty * 0.4) + (conflicting_penalty * 0.2)),
        )

        # Build updated assessment
        updated_assessment = InvestigationAssessment(
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            uncertainty=round(calculated_uncertainty, 3),
            fraud_type=assessment.fraud_type,
            confidence=round(max(0.0, 1.0 - calculated_uncertainty), 3),
            rationale=assessment.rationale,
        )
        updated["assessment"] = updated_assessment

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.UNCERTAINTY_ASSESSED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.ASSESS_UNCERTAINTY,
            message=f"Uncertainty assessed at {calculated_uncertainty:.2f} (missing sources: {sorted(missing_sources)})",
            payload={
                "uncertainty": calculated_uncertainty,
                "missing_sources": list(missing_sources),
                "evidence_count": len(evidence_list),
                "pattern_count": len(patterns),
            },
            created_at=datetime.now(UTC),
        )
        updated["events"] = [*updated.get("events", []), event]

        threshold = getattr(self.settings, "agent_uncertainty_threshold", 0.40)
        if calculated_uncertainty > threshold and not is_step_limit_reached(updated):
            updated["current_stage"] = AgentStage.REQUEST_EVIDENCE
        else:
            updated["current_stage"] = AgentStage.RECOMMEND_ACTION

        return updated
