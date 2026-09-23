from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

from backend.app.config import Settings

# ---------------------------------------------------------------------------
# Context variables carried through the investigation lifecycle
# ---------------------------------------------------------------------------

_investigation_id_var: ContextVar[str] = ContextVar(
    "investigation_id", default=""
)
_case_id_var: ContextVar[str] = ContextVar("case_id", default="")
_stage_var: ContextVar[str] = ContextVar("stage", default="")


def bind_investigation_context(
    *,
    investigation_id: str = "",
    case_id: str = "",
    stage: str = "",
) -> None:
    if investigation_id:
        _investigation_id_var.set(investigation_id)
    if case_id:
        _case_id_var.set(case_id)
    if stage:
        _stage_var.set(stage)


def clear_investigation_context() -> None:
    _investigation_id_var.set("")
    _case_id_var.set("")
    _stage_var.set("")


def _add_investigation_context(
    logger: Any,
    method: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    inv_id = _investigation_id_var.get()
    case_id = _case_id_var.get()
    stage = _stage_var.get()

    if inv_id:
        event_dict["investigation_id"] = inv_id
    if case_id:
        event_dict["case_id"] = case_id
    if stage:
        event_dict["stage"] = stage

    return event_dict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def configure_logging(settings: Settings) -> None:
    """Configure structlog for the application."""

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _add_investigation_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_json:
        shared_processors.append(
            structlog.processors.dict_tracebacks,
        )
        final_processor: Any = structlog.processors.JSONRenderer()
    else:
        shared_processors.append(
            structlog.dev.set_exc_info,
        )
        final_processor = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=final_processor,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    for noisy_logger in (
        "uvicorn.access",
        "httpx",
        "httpcore",
    ):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> Any:
    """Return a structlog-bound logger."""
    return structlog.get_logger(name)
