"""
Agent-facing policy tools.

Provides policy and authorization checks for proposed fraud actions while
keeping the actual policy logic inside the NBA constraint layer.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from backend.nba.constraints import ActionConstraintEngine


class PolicyTools:
    """Interface for policy checks available to the agent."""

    def __init__(
        self,
        engine: ActionConstraintEngine | None = None,
    ) -> None:
        self.engine = engine or ActionConstraintEngine()

    def check_action(
        self,
        action: str,
        *,
        evidence: Sequence[Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> Any:
        """
        Check whether a proposed action satisfies configured constraints.
        """
        evidence_items = list(evidence or [])
        context_data = dict(context or {})

        for method_name in ("check", "evaluate", "validate"):
            method = getattr(self.engine, method_name, None)
            if method is not None:
                try:
                    return method(
                        action,
                        evidence=evidence_items,
                        context=context_data,
                    )
                except TypeError:
                    try:
                        return method(
                            action,
                            evidence_items,
                            context_data,
                        )
                    except TypeError:
                        return method(action)

        raise AttributeError(
            "ActionConstraintEngine does not expose a supported "
            "policy-check method."
        )

    def is_allowed(
        self,
        action: str,
        *,
        evidence: Sequence[Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> bool:
        """Return a simple boolean policy decision."""
        result = self.check_action(
            action,
            evidence=evidence,
            context=context,
        )

        if isinstance(result, bool):
            return result

        for attribute in ("allowed", "is_allowed", "permitted"):
            value = getattr(result, attribute, None)
            if value is not None:
                return bool(value)

        if isinstance(result, Mapping):
            for key in ("allowed", "is_allowed", "permitted"):
                if key in result:
                    return bool(result[key])

        return False

    def explain(
        self,
        action: str,
        *,
        evidence: Sequence[Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a normalized policy explanation."""
        result = self.check_action(
            action,
            evidence=evidence,
            context=context,
        )

        if hasattr(result, "to_dict"):
            return result.to_dict()

        if hasattr(result, "model_dump"):
            return result.model_dump()

        if isinstance(result, Mapping):
            return dict(result)

        return {
            "action": action,
            "allowed": self.is_allowed(
                action,
                evidence=evidence,
                context=context,
            ),
            "result": result,
        }


def create_policy_tools(
    engine: ActionConstraintEngine | None = None,
) -> PolicyTools:
    """Create the default policy-tool collection."""
    return PolicyTools(engine=engine)