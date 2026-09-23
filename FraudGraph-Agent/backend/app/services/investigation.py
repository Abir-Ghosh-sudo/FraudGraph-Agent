from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from threading import RLock
from typing import Any
from uuid import uuid4

from backend.agent.agent import FraudInvestigationAgent
from backend.agent.state import AgentRuntimeState
from backend.app.config import Settings
from backend.app.errors import InvestigationNotFoundError
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEvent
from backend.app.schemas.investigation import (
    Investigation,
    InvestigationAssessment,
    InvestigationCreate,
    InvestigationProgress,
    InvestigationResult,
    InvestigationStatus,
)
from backend.app.streaming import EventStreamManager

logger = get_logger("app.services.investigation")


class InvestigationService:
    """Manages investigation lifecycle, agent execution, state synchronization, and SSE event dispatch."""

    def __init__(
        self,
        settings: Settings,
        agent: FraudInvestigationAgent | None = None,
        stream_manager: EventStreamManager | None = None,
    ) -> None:
        self.settings = settings
        self.agent = agent or FraudInvestigationAgent(settings=settings)
        self.stream_manager = stream_manager or EventStreamManager()
        self._investigations: dict[str, Investigation] = {}
        self._events: dict[str, list[AgentEvent]] = {}
        self._states: dict[str, AgentRuntimeState] = {}
        self._lock = RLock()

    def create(self, payload: InvestigationCreate) -> Investigation:
        now = datetime.now(UTC)
        investigation_id = f"inv_{uuid4().hex[:16]}"

        investigation = Investigation(
            investigation_id=investigation_id,
            status=InvestigationStatus.PENDING,
            trigger=payload.trigger,
            progress=InvestigationProgress(
                max_steps=self.settings.agent_max_steps,
                current_stage="trigger",
                message="Investigation created and pending execution.",
            ),
            created_at=now,
            updated_at=now,
        )

        with self._lock:
            self._investigations[investigation_id] = investigation
            self._events[investigation_id] = []

        logger.info("investigation_created", investigation_id=investigation_id)
        return investigation

    def get(self, investigation_id: str) -> Investigation | None:
        with self._lock:
            return self._investigations.get(investigation_id)

    def list(self) -> list[Investigation]:
        with self._lock:
            return list(self._investigations.values())

    def get_events(self, investigation_id: str) -> list[AgentEvent]:
        with self._lock:
            return list(self._events.get(investigation_id, []))

    def get_state(self, investigation_id: str) -> AgentRuntimeState | None:
        with self._lock:
            return self._states.get(investigation_id) or self.agent.get_state(investigation_id)

    def get_result(self, investigation_id: str) -> InvestigationResult | None:
        investigation = self.get(investigation_id)
        if investigation is None:
            return None
        return investigation.result

    def start(self, investigation_id: str) -> Investigation:
        investigation = self.get(investigation_id)
        if investigation is None:
            raise InvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

        investigation.status = InvestigationStatus.INVESTIGATING
        investigation.updated_at = datetime.now(UTC)

        trigger_data = (
            investigation.trigger.model_dump()
            if hasattr(investigation.trigger, "model_dump")
            else dict(investigation.trigger)
        )

        # Run agent workflow
        final_state = self.agent.start(
            investigation_id=investigation_id,
            trigger=trigger_data,
        )

        return self._sync_final_state(investigation_id, final_state)

    async def astart(self, investigation_id: str) -> Investigation:
        investigation = self.get(investigation_id)
        if investigation is None:
            raise InvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

        investigation.status = InvestigationStatus.INVESTIGATING
        investigation.updated_at = datetime.now(UTC)

        trigger_data = (
            investigation.trigger.model_dump()
            if hasattr(investigation.trigger, "model_dump")
            else dict(investigation.trigger)
        )

        # Run agent workflow asynchronously
        final_state = await self.agent.astart(
            investigation_id=investigation_id,
            trigger=trigger_data,
        )

        synced = self._sync_final_state(investigation_id, final_state)

        # Broadcast events to SSE subscribers
        events = final_state.get("events", [])
        for ev in events:
            await self.stream_manager.publish(investigation_id, ev)

        return synced

    def _sync_final_state(
        self,
        investigation_id: str,
        final_state: AgentRuntimeState,
    ) -> Investigation:
        with self._lock:
            investigation = self._investigations.get(investigation_id)
            if investigation is None:
                raise InvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            self._states[investigation_id] = final_state
            raw_events = final_state.get("events", [])
            self._events[investigation_id] = list(raw_events)

            now = datetime.now(UTC)
            investigation.status = final_state.get("status", InvestigationStatus.COMPLETED)
            investigation.updated_at = now
            investigation.completed_at = final_state.get("completed_at") or (
                now if investigation.status == InvestigationStatus.COMPLETED else None
            )
            investigation.case_id = final_state.get("case_id")

            # Sync assessment
            state_assessment = final_state.get("assessment")
            if isinstance(state_assessment, InvestigationAssessment):
                investigation.assessment = state_assessment
            elif isinstance(state_assessment, dict):
                investigation.assessment = InvestigationAssessment(**state_assessment)

            # Sync progress
            completed_stages = list(
                {
                    str(getattr(e, "stage", ""))
                    for e in raw_events
                    if getattr(e, "stage", "")
                }
            )
            investigation.progress = InvestigationProgress(
                step=final_state.get("step", 0),
                max_steps=final_state.get("max_steps", self.settings.agent_max_steps),
                current_stage=str(final_state.get("current_stage", "complete")),
                message="Workflow execution finished.",
                completed_stages=completed_stages,
            )

            # Sync result
            explanation = final_state.get("explanation")
            findings = list(explanation.reasoning_points) if explanation else []
            recommendations: list[str] = []
            selected_action = final_state.get("selected_action")
            if selected_action:
                recommendations.append(selected_action.title)

            evidence_ids = [
                str(getattr(e, "evidence_id", ""))
                for e in final_state.get("evidence", [])
                if getattr(e, "evidence_id", "")
            ]

            requires_additional = bool(final_state.get("evidence_requests"))
            required_ev = []
            for req in final_state.get("evidence_requests", []):
                required_ev.extend(getattr(req, "requested_evidence", []))

            investigation.result = InvestigationResult(
                findings=findings,
                recommendations=recommendations,
                evidence_ids=evidence_ids,
                related_case_ids=[
                    str(c.get("case_id", ""))
                    for c in final_state.get("related_cases", [])
                    if c.get("case_id")
                ],
                requires_additional_evidence=requires_additional,
                required_evidence=required_ev,
            )

            # Publish sync events to stream manager
            for ev in raw_events:
                self.stream_manager.publish_sync(investigation_id, ev)

            return investigation