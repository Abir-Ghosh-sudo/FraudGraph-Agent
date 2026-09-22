from __future__ import annotations

from collections.abc import Generator

from backend.app.config import Settings, get_settings


# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

def get_app_settings() -> Settings:
    """
    FastAPI dependency for application settings.

    The Settings object is cached by get_settings(), so all requests use
    the same configuration instance during the application lifetime.
    """

    return get_settings()


# ============================================================================
# RUNTIME INITIALIZATION
# ============================================================================

def initialize_runtime(settings: Settings) -> None:
    """
    Prepare application-owned runtime directories.

    This function only creates empty directories required by the application.

    It does NOT:
        - load the HHGOA dataset
        - create fake data
        - seed demo cases
        - connect to external action systems
        - run model training
    """

    settings.ensure_runtime_directories()


# ============================================================================
# SIMPLE RUNTIME CONTEXT
# ============================================================================

class ApplicationContext:
    """
    Lightweight application dependency container.

    More services will be attached here as the architecture is implemented.

    Keeping the context small at this stage prevents circular dependencies
    between FastAPI, the agent, TigerGraph and individual services.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings


def get_application_context(
    settings: Settings | None = None,
) -> ApplicationContext:
    """
    Build the current application context.

    A future version will populate this context with shared infrastructure
    such as:

        - TigerGraph client
        - GraphRAG retriever
        - policy engine
        - case memory service
        - agent runtime

    Those components are intentionally not imported yet because their
    implementations have not been created.
    """

    resolved_settings = settings or get_settings()

    return ApplicationContext(
        settings=resolved_settings,
    )


# ============================================================================
# DEPENDENCY GENERATOR
# ============================================================================

def application_context_dependency() -> Generator[
    ApplicationContext,
    None,
    None,
]:
    """
    FastAPI-compatible dependency generator.

    This gives API routes a single entry point for accessing application
    infrastructure.
    """

    context = get_application_context()

    try:
        yield context
    finally:
        # Currently there are no resources to close.
        #
        # Later this is where shared resources can be cleaned up if needed.
        pass