"""
Agent-facing tools for fraud investigation case management.

These wrappers expose the existing CaseService to agent nodes while keeping
case lifecycle, findings, evidence, and decision logic inside the cases
domain.
"""

from __future__ import annotations

from typing import Any

from backend.cases.service import CaseService


class CaseTools:
    """Guarded interface for agent case-management operations."""

    def __init__(self, service: CaseService | None = None) -> None:
        self.service = service or CaseService()

    def create_case(
        self,
        *,
        case_id: str,
        investigation_id: str | None = None,
        title: str | None = None,
    ) -> Any:
        """Create a case through the existing case service."""
        create_method = getattr(self.service, "create_case", None)

        if create_method is None:
            raise AttributeError(
                "CaseService does not expose create_case()."
            )

        return create_method(
            case_id=case_id,
            investigation_id=investigation_id,
            title=title,
        )

    def get_case(self, case_id: str) -> Any:
        """Retrieve a case snapshot."""
        for method_name in ("get_case", "get", "snapshot"):
            method = getattr(self.service, method_name, None)
            if method is not None:
                return method(case_id)

        raise AttributeError(
            "CaseService does not expose a supported case retrieval method."
        )

    def add_finding(
        self,
        case_id: str,
        finding: Any,
    ) -> Any:
        """Attach a finding to an existing case."""
        for method_name in ("add_finding", "record_finding"):
            method = getattr(self.service, method_name, None)
            if method is not None:
                return method(case_id, finding)

        raise AttributeError(
            "CaseService does not expose a finding operation."
        )

    def add_evidence(
        self,
        case_id: str,
        evidence: Any,
    ) -> Any:
        """Attach evidence to an existing case."""
        for method_name in ("add_evidence", "record_evidence"):
            method = getattr(self.service, method_name, None)
            if method is not None:
                return method(case_id, evidence)

        raise AttributeError(
            "CaseService does not expose an evidence operation."
        )

    def record_decision(
        self,
        case_id: str,
        decision: Any,
    ) -> Any:
        """Record an agent or analyst decision."""
        for method_name in ("record_decision", "add_decision"):
            method = getattr(self.service, method_name, None)
            if method is not None:
                return method(case_id, decision)

        raise AttributeError(
            "CaseService does not expose a decision operation."
        )

    def transition(
        self,
        case_id: str,
        status: Any,
        *,
        reason: str | None = None,
    ) -> Any:
        """Transition the case through the existing lifecycle service."""
        for method_name in ("transition", "transition_case"):
            method = getattr(self.service, method_name, None)
            if method is not None:
                return method(
                    case_id,
                    status,
                    reason=reason,
                )

        raise AttributeError(
            "CaseService does not expose a case transition operation."
        )

    def summary(self, case_id: str) -> dict[str, Any]:
        """Return a compact case summary for agent reasoning."""
        case = self.get_case(case_id)

        if hasattr(case, "model_dump"):
            return case.model_dump()

        if hasattr(case, "to_dict"):
            return case.to_dict()

        if isinstance(case, dict):
            return dict(case)

        if hasattr(case, "__dict__"):
            return dict(case.__dict__)

        return {"case": case}


def create_case_tools(
    service: CaseService | None = None,
) -> CaseTools:
    """Create the default case-tool collection."""
    return CaseTools(service=service)