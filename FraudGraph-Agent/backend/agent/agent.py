from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Any

from backend.agent.state import (
    AgentRuntimeState,
    create_initial_state,
)
from backend.agent.workflow import compile_workflow
from backend.app.config import Settings
from backend.app.schemas.agent import AgentEvent, AgentEventType, AgentStage
from backend.app.schemas.investigation import (
    InvestigationStatus,
)


class FraudInvestigationAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._workflow = compile_workflow(settings)
        self._states: dict[str, AgentRuntimeState] = {}
        self._lock = RLock()

    def start(
        self,
        investigation_id: str,
        trigger: dict[str, Any],
    ) -> AgentRuntimeState:
        state = create_initial_state(
            investigation_id=investigation_id,
            trigger=trigger,
            max_steps=self.settings.agent_max_steps,
        )

        state["status"] = InvestigationStatus.INVESTIGATING

        event = self._event(
            state=state,
            event_type=AgentEventType.INVESTIGATION_STARTED,
            stage=AgentStage.TRIGGER,
            message="Fraud investigation started.",
        )

        state["events"] = [event]

        with self._lock:
            self._states[investigation_id] = state

        return self._run(investigation_id, state)

    async def astart(
        self,
        investigation_id: str,
        trigger: dict[str, Any],
    ) -> AgentRuntimeState:
        import asyncio

        return await asyncio.to_thread(
            self.start,
            investigation_id=investigation_id,
            trigger=trigger,
        )

    def get_state(
        self,
        investigation_id: str,
    ) -> AgentRuntimeState | None:
        with self._lock:
            return self._states.get(investigation_id)

    def get_events(
        self,
        investigation_id: str,
    ) -> list[AgentEvent]:
        state = self.get_state(investigation_id)

        if state is None:
            return []

        return list(state.get("events", []))

    def _run(
        self,
        investigation_id: str,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        try:
            result = self._workflow.invoke(state)

            if not isinstance(result, dict):
                raise TypeError(
                    "Agent workflow returned an invalid state."
                )

            final_state = self._normalize_result(
                investigation_id=investigation_id,
                result=result,
            )

        except Exception as exc:
            final_state = self._handle_failure(
                state=state,
                error=exc,
            )

        with self._lock:
            self._states[investigation_id] = final_state

        return final_state

    def _normalize_result(
        self,
        investigation_id: str,
        result: dict[str, Any],
    ) -> AgentRuntimeState:
        state = dict(result)

        state["investigation_id"] = investigation_id
        current_status = state.get("status")
        if current_status not in (
            InvestigationStatus.AWAITING_APPROVAL,
            InvestigationStatus.AWAITING_EVIDENCE,
        ):
            state["status"] = InvestigationStatus.COMPLETED

        state["current_stage"] = AgentStage.COMPLETE
        state["updated_at"] = datetime.now(UTC)

        if state.get("completed_at") is None:
            state["completed_at"] = state["updated_at"]

        events = list(state.get("events", []))
        if not any(
            getattr(e, "event_type", "") == AgentEventType.INVESTIGATION_COMPLETED
            for e in events
        ):
            events.append(
                self._event(
                    state=state,
                    event_type=AgentEventType.INVESTIGATION_COMPLETED,
                    stage=AgentStage.COMPLETE,
                    message="Fraud investigation workflow completed.",
                )
            )

        state["events"] = events

        return state

    def _handle_failure(
        self,
        state: AgentRuntimeState,
        error: Exception,
    ) -> AgentRuntimeState:
        now = datetime.now(UTC)
        message = str(error).strip() or type(error).__name__

        updated = dict(state)

        updated["status"] = InvestigationStatus.FAILED
        updated["current_stage"] = AgentStage.COMPLETE
        updated["updated_at"] = now
        updated["completed_at"] = now
        updated["errors"] = [
            *state.get("errors", []),
            message,
        ]

        events = list(state.get("events", []))

        events.append(
            self._event(
                state=updated,
                event_type=AgentEventType.INVESTIGATION_FAILED,
                stage=AgentStage.COMPLETE,
                message=f"Investigation failed: {message}",
            )
        )

        updated["events"] = events

        return updated

    @staticmethod
    def _event(
        state: AgentRuntimeState,
        event_type: AgentEventType,
        stage: AgentStage,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> AgentEvent:
        return AgentEvent(
            event_id=f"evt_{datetime.now(UTC).timestamp():.6f}",
            event_type=event_type,
            investigation_id=state["investigation_id"],
            case_id=state.get("case_id"),
            stage=stage,
            message=message,
            payload=payload or {},
            created_at=datetime.now(UTC),
        )