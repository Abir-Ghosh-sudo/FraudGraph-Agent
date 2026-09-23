from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus
from backend.app.services.memory import MemoryService

logger = get_logger("agent.nodes.update_memory")


class UpdateMemoryNode:
    """Stores completed investigation outcomes in case memory and marks investigation completion."""

    def __init__(
        self,
        settings: Settings,
        memory_service: MemoryService | None = None,
    ) -> None:
        self.settings = settings
        self.memory_service = memory_service or MemoryService(settings=settings)

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.COMPLETE)

        investigation_id = updated.get("investigation_id", "")
        case_id = updated.get("case_id") or f"case_{investigation_id[:12]}"
        now = datetime.now(UTC)
        updated["completed_at"] = now

        # Only set status to COMPLETED if not awaiting approval or awaiting evidence
        current_status = updated.get("status")
        if current_status not in (InvestigationStatus.AWAITING_APPROVAL, InvestigationStatus.AWAITING_EVIDENCE):
            updated["status"] = InvestigationStatus.COMPLETED

        # Collect findings from explanation or patterns
        explanation = updated.get("explanation")
        findings = list(explanation.reasoning_points) if explanation else []
        if not findings:
            for p in updated.get("detected_patterns", []):
                findings.append(p.get("description", "Fraud pattern detected"))

        # Collect decisions and actions
        decisions = [d.decision for d in updated.get("decisions", [])]
        selected_action = updated.get("selected_action")
        actions = [selected_action.title] if selected_action else []

        assessment = updated.get("assessment")
        outcome = assessment.risk_level.value if assessment and hasattr(assessment.risk_level, "value") else "unknown"

        # Store in MemoryService
        if self.settings.case_memory_enabled:
            try:
                mem_id = self.memory_service.store(
                    case_id=case_id,
                    investigation_id=investigation_id,
                    outcome=outcome,
                    findings=findings,
                    decisions=decisions,
                    actions=actions,
                    metadata={
                        "risk_score": getattr(assessment, "risk_score", None),
                        "fraud_type": getattr(assessment, "fraud_type", None),
                    },
                )
                if mem_id:
                    event = AgentEvent(
                        event_id=str(uuid4()),
                        event_type=AgentEventType.MEMORY_UPDATED,
                        investigation_id=investigation_id,
                        case_id=case_id,
                        stage=AgentStage.UPDATE_MEMORY,
                        message=f"Investigation results indexed in case memory (id={mem_id}).",
                        payload={"memory_id": mem_id},
                        created_at=now,
                    )
                    updated["events"] = [*updated.get("events", []), event]
            except Exception as exc:
                logger.warning("failed_storing_case_memory", error=str(exc))

        completed_event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.INVESTIGATION_COMPLETED,
            investigation_id=investigation_id,
            case_id=case_id,
            stage=AgentStage.COMPLETE,
            message="Fraud investigation workflow completed successfully.",
            payload={
                "status": updated.get("status", InvestigationStatus.COMPLETED).value
                if hasattr(updated.get("status"), "value")
                else str(updated.get("status")),
                "step_count": updated.get("step", 0),
            },
            created_at=now,
        )
        updated["events"] = [*updated.get("events", []), completed_event]

        return updated
