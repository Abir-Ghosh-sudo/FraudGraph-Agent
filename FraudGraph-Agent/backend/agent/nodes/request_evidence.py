from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ApprovalRoute
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage, EvidenceRequest
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger("agent.nodes.request_evidence")


class RequestEvidenceNode:
    """Generates an EvidenceRequest when uncertainty exceeds threshold."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.REQUEST_EVIDENCE)

        evidence_list = updated.get("evidence", [])
        existing_sources = {getattr(e, "source_type", "") for e in evidence_list}
        needed_sources = [s for s in ["device_fingerprint", "ip_geolocation", "customer_kyc", "card_history"] if s not in existing_sources]
        if not needed_sources:
            needed_sources = ["additional_transaction_context"]

        evidence_ids = [getattr(e, "evidence_id", "") for e in evidence_list if getattr(e, "evidence_id", "")]

        request = EvidenceRequest(
            request_id=f"req_{uuid4().hex[:12]}",
            reason="High uncertainty detected during risk assessment; supplementary data sources required.",
            requested_evidence=needed_sources,
            evidence_ids=evidence_ids[:10],
            approval_required=False,
            approval_route=ApprovalRoute.ANALYST.value,
            created_at=datetime.now(UTC),
        )

        requests = list(updated.get("evidence_requests", []))
        requests.append(request)
        updated["evidence_requests"] = requests
        updated["status"] = InvestigationStatus.AWAITING_EVIDENCE

        event = AgentEvent(
            event_id=str(uuid4()),
            event_type=AgentEventType.EVIDENCE_REQUESTED,
            investigation_id=updated.get("investigation_id", ""),
            case_id=updated.get("case_id"),
            stage=AgentStage.REQUEST_EVIDENCE,
            message=f"Requested additional evidence sources: {', '.join(needed_sources)}",
            payload={
                "request_id": request.request_id,
                "requested_sources": needed_sources,
            },
            created_at=datetime.now(UTC),
        )
        updated["events"] = [*updated.get("events", []), event]

        return updated
