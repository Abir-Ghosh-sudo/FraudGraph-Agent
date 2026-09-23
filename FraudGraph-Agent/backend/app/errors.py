from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ============================================================================
# BASE ERRORS
# ============================================================================

class FraudGraphError(RuntimeError):
    """Base error for all FraudGraph-Agent domain failures."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, *, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.detail is not None:
            result["detail"] = self.detail
        return result


# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================

class ConfigurationError(FraudGraphError):
    """Raised when required infrastructure is not configured."""

    status_code = 503
    error_code = "configuration_error"


class DatasetNotConfiguredError(ConfigurationError):
    """Raised when the HHGOA dataset files are not available."""

    error_code = "dataset_not_configured"


class TigerGraphNotConfiguredError(ConfigurationError):
    """Raised when TigerGraph credentials/host are not set."""

    error_code = "tigergraph_not_configured"


class LLMNotConfiguredError(ConfigurationError):
    """Raised when the LLM provider is not available."""

    error_code = "llm_not_configured"


# ============================================================================
# DATASET ERRORS
# ============================================================================

class DatasetError(FraudGraphError):
    """Raised when HHGOA dataset operations fail."""

    status_code = 500
    error_code = "dataset_error"


class DatasetSchemaError(DatasetError):
    """Raised when the dataset schema is missing required columns."""

    error_code = "dataset_schema_error"


class DatasetFileError(DatasetError):
    """Raised when a dataset file cannot be read."""

    error_code = "dataset_file_error"


# ============================================================================
# GRAPH / TIGERGRAPH ERRORS
# ============================================================================

class GraphError(FraudGraphError):
    """Raised when graph operations fail."""

    status_code = 502
    error_code = "graph_error"


class GraphQueryError(GraphError):
    """Raised when a TigerGraph query fails."""

    error_code = "graph_query_error"


class GraphEntityNotFoundError(GraphError):
    """Raised when a graph entity cannot be found."""

    status_code = 404
    error_code = "graph_entity_not_found"


# ============================================================================
# EVIDENCE ERRORS
# ============================================================================

class EvidenceError(FraudGraphError):
    """Raised when evidence operations fail."""

    status_code = 500
    error_code = "evidence_error"


class EvidenceNotFoundError(EvidenceError):
    """Raised when requested evidence does not exist."""

    status_code = 404
    error_code = "evidence_not_found"


# ============================================================================
# INVESTIGATION ERRORS
# ============================================================================

class InvestigationError(FraudGraphError):
    """Raised when investigation operations fail."""

    status_code = 500
    error_code = "investigation_error"


class InvestigationNotFoundError(InvestigationError):
    """Raised when a requested investigation does not exist."""

    status_code = 404
    error_code = "investigation_not_found"


class InvestigationAlreadyRunningError(InvestigationError):
    """Raised when an investigation is already in progress."""

    status_code = 409
    error_code = "investigation_already_running"


# ============================================================================
# CASE ERRORS
# ============================================================================

class CaseError(FraudGraphError):
    """Raised when case operations fail."""

    status_code = 500
    error_code = "case_error"


class CaseNotFoundError(CaseError):
    """Raised when a requested case does not exist."""

    status_code = 404
    error_code = "case_not_found"


class CaseStatusTransitionError(CaseError):
    """Raised when a case status transition is invalid."""

    status_code = 422
    error_code = "case_status_transition_error"


# ============================================================================
# POLICY ERRORS
# ============================================================================

class PolicyError(FraudGraphError):
    """Raised when policy evaluation fails."""

    status_code = 500
    error_code = "policy_error"


class PolicyNotFoundError(PolicyError):
    """Raised when a requested policy document does not exist."""

    status_code = 404
    error_code = "policy_not_found"


# ============================================================================
# LLM ERRORS
# ============================================================================

class LLMError(FraudGraphError):
    """Raised when LLM interaction fails."""

    status_code = 503
    error_code = "llm_error"


class LLMTimeoutError(LLMError):
    """Raised when the LLM request times out."""

    error_code = "llm_timeout"


class LLMOutputValidationError(LLMError):
    """Raised when LLM output fails Pydantic validation."""

    error_code = "llm_output_invalid"


# ============================================================================
# ACTION ERRORS
# ============================================================================

class ActionError(FraudGraphError):
    """Raised when action operations fail."""

    status_code = 500
    error_code = "action_error"


class ActionNotFoundError(ActionError):
    """Raised when a requested action does not exist."""

    status_code = 404
    error_code = "action_not_found"


class ActionNotPermittedError(ActionError):
    """Raised when action execution is not permitted by configuration."""

    status_code = 403
    error_code = "action_not_permitted"


# ============================================================================
# APPROVAL ERRORS
# ============================================================================

class ApprovalError(FraudGraphError):
    """Raised when approval operations fail."""

    status_code = 500
    error_code = "approval_error"


class ApprovalNotFoundError(ApprovalError):
    """Raised when a requested approval does not exist."""

    status_code = 404
    error_code = "approval_not_found"


class ApprovalRequiredError(ApprovalError):
    """Raised when an action requires human approval before execution."""

    status_code = 403
    error_code = "approval_required"


# ============================================================================
# MEMORY ERRORS
# ============================================================================

class MemoryError(FraudGraphError):
    """Raised when case memory operations fail."""

    status_code = 500
    error_code = "memory_error"


class MemoryNotFoundError(MemoryError):
    """Raised when a memory entry does not exist."""

    status_code = 404
    error_code = "memory_not_found"


# ============================================================================
# BENCHMARK ERRORS
# ============================================================================

class BenchmarkError(FraudGraphError):
    """Raised when benchmark operations fail."""

    status_code = 500
    error_code = "benchmark_error"


class BenchmarkNotConfiguredError(BenchmarkError):
    """Raised when benchmark cases are not available."""

    status_code = 503
    error_code = "benchmark_not_configured"


# ============================================================================
# FASTAPI EXCEPTION HANDLERS
# ============================================================================

def _error_response(
    exc: FraudGraphError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all domain exception handlers on the FastAPI app."""

    @app.exception_handler(FraudGraphError)
    async def handle_fraud_graph_error(
        request: Request,
        exc: FraudGraphError,
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(ConfigurationError)
    async def handle_configuration_error(
        request: Request,
        exc: ConfigurationError,
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(InvestigationNotFoundError)
    async def handle_investigation_not_found(
        request: Request,
        exc: InvestigationNotFoundError,
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(CaseNotFoundError)
    async def handle_case_not_found(
        request: Request,
        exc: CaseNotFoundError,
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(ActionNotPermittedError)
    async def handle_action_not_permitted(
        request: Request,
        exc: ActionNotPermittedError,
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(ApprovalRequiredError)
    async def handle_approval_required(
        request: Request,
        exc: ApprovalRequiredError,
    ) -> JSONResponse:
        return _error_response(exc)
