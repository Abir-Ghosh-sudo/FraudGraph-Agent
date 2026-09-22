from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.app.config import Settings
from backend.app.schemas.investigation import (
    Investigation,
    InvestigationCreate,
    InvestigationProgress,
    InvestigationStatus,
)


class InvestigationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._investigations: dict[str, Investigation] = {}

    def create(
        self,
        payload: InvestigationCreate,
    ) -> Investigation:
        now = datetime.now(UTC)
        investigation_id = f"inv_{uuid4().hex}"

        investigation = Investigation(
            investigation_id=investigation_id,
            status=InvestigationStatus.PENDING,
            trigger=payload.trigger,
            progress=InvestigationProgress(
                max_steps=self.settings.agent_max_steps,
            ),
            created_at=now,
            updated_at=now,
        )

        self._investigations[investigation_id] = investigation

        return investigation

    def get(
        self,
        investigation_id: str,
    ) -> Investigation | None:
        return self._investigations.get(investigation_id)

    def list(self) -> list[Investigation]:
        return list(self._investigations.values())

    def update_progress(
        self,
        investigation_id: str,
        progress: InvestigationProgress,
    ) -> Investigation | None:
        investigation = self._investigations.get(investigation_id)

        if investigation is None:
            return None

        investigation.progress = progress
        investigation.updated_at = datetime.now(UTC)

        return investigation

    def update_status(
        self,
        investigation_id: str,
        status: InvestigationStatus,
    ) -> Investigation | None:
        investigation = self._investigations.get(investigation_id)

        if investigation is None:
            return None

        now = datetime.now(UTC)

        investigation.status = status
        investigation.updated_at = now

        if status == InvestigationStatus.COMPLETED:
            investigation.completed_at = now

        return investigation