from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger("agent.nodes.reassess")


class ReassessNode:
    """Prepares state for re-evaluation following evidence request, clearing transient blockers."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.REASSESS)
        updated["status"] = InvestigationStatus.INVESTIGATING

        # Mark reassessment counter in metadata
        metadata = dict(updated.get("metadata", {}))
        reassess_count = metadata.get("reassess_count", 0) + 1
        metadata["reassess_count"] = reassess_count
        updated["metadata"] = metadata

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.STAGE_STARTED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.REASSESS,
            message=f"Reassessment iteration {reassess_count} started.",
            payload={"reassess_count": reassess_count},
            created_at=datetime.now(UTC),
        )
        updated["events"] = [*updated.get("events", []), event]

        return updated
