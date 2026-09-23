from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends

from backend.agent.agent import FraudInvestigationAgent
from backend.app.config import Settings, get_settings
from backend.app.services.case import CaseService
from backend.app.services.evidence import EvidenceService
from backend.app.services.graph import GraphService
from backend.app.services.investigation import InvestigationService
from backend.app.services.memory import MemoryService
from backend.app.streaming import EventStreamManager
from backend.policy.engine import PolicyEngine


# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

def get_app_settings() -> Settings:
    """FastAPI dependency for application settings."""
    return get_settings()


# ============================================================================
# RUNTIME INITIALIZATION
# ============================================================================

def initialize_runtime(settings: Settings) -> None:
    """Prepare application-owned runtime directories."""
    settings.ensure_runtime_directories()


# ============================================================================
# APPLICATION CONTEXT
# ============================================================================

class ApplicationContext:
    """Shared application dependency container containing singleton service instances."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.graph_service = GraphService(settings=settings)
        self.evidence_service = EvidenceService(settings=settings)
        self.case_service = CaseService(settings=settings)
        self.memory_service = MemoryService(settings=settings)
        self.policy_engine = PolicyEngine(settings=settings)
        self.stream_manager = EventStreamManager()
        self.agent = FraudInvestigationAgent(settings=settings)
        self.investigation_service = InvestigationService(
            settings=settings,
            agent=self.agent,
            stream_manager=self.stream_manager,
        )


_APP_CONTEXT: ApplicationContext | None = None


def get_application_context(
    settings: Settings | None = None,
) -> ApplicationContext:
    """Build or return the singleton application context."""
    global _APP_CONTEXT
    if _APP_CONTEXT is None:
        resolved_settings = settings or get_settings()
        _APP_CONTEXT = ApplicationContext(settings=resolved_settings)
    return _APP_CONTEXT


def application_context_dependency() -> Generator[ApplicationContext, None, None]:
    """FastAPI-compatible dependency generator."""
    context = get_application_context()
    try:
        yield context
    finally:
        pass


def get_investigation_service(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> InvestigationService:
    return ctx.investigation_service


def get_case_service(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> CaseService:
    return ctx.case_service


def get_evidence_service(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> EvidenceService:
    return ctx.evidence_service


def get_memory_service(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> MemoryService:
    return ctx.memory_service


def get_policy_engine(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> PolicyEngine:
    return ctx.policy_engine


def get_graph_service(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> GraphService:
    return ctx.graph_service


def get_stream_manager(
    ctx: ApplicationContext = Depends(application_context_dependency),
) -> EventStreamManager:
    return ctx.stream_manager