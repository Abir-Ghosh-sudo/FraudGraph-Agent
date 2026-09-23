"""
Action execution layer for the fraud investigation agent.

The executor is responsible for:
- validating an action against the ActionRegistry,
- enforcing approval requirements,
- invoking an explicitly registered handler,
- returning a structured execution result,
- preventing accidental execution of unregistered actions.

Real-world integrations should be injected as handlers into the registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from backend.actions.registry import ActionDefinition, ActionRegistry


ActionHandler = Callable[[Mapping[str, Any]], Any]


@dataclass(slots=True)
class ActionExecutionResult:
    """Result of an attempted action execution."""

    action: str
    success: bool
    executed: bool
    approval_required: bool
    approval_granted: bool
    message: str
    result: Any = None
    error: str | None = None
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "action": self.action,
            "success": self.success,
            "executed": self.executed,
            "approval_required": self.approval_required,
            "approval_granted": self.approval_granted,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "executed_at": self.executed_at.isoformat(),
        }


class ActionExecutor:
    """
    Safely executes actions registered in an ActionRegistry.

    The executor intentionally does not invent handlers. An action without
    an explicitly registered handler remains non-executable.
    """

    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    def get_definition(self, action: str) -> ActionDefinition:
        """Return the registered action definition."""
        return self.registry.require(action)

    def can_execute(
        self,
        action: str,
        *,
        approval_granted: bool = False,
    ) -> tuple[bool, str]:
        """
        Determine whether an action may be executed.

        Approval is required when the action definition says so. A missing
        handler always prevents execution.
        """
        try:
            definition = self.get_definition(action)
        except (KeyError, ValueError) as exc:
            return False, str(exc)

        if definition.handler is None:
            return False, f"No execution handler registered for action '{action}'."

        if definition.requires_approval and not approval_granted:
            return False, f"Approval is required before executing '{action}'."

        return True, "Action is authorized for execution."

    def execute(
        self,
        action: str,
        payload: Mapping[str, Any] | None = None,
        *,
        approval_granted: bool = False,
    ) -> ActionExecutionResult:
        """
        Execute a registered action.

        Parameters
        ----------
        action:
            Registered action identifier.
        payload:
            Input passed to the action handler.
        approval_granted:
            Explicit approval state supplied by the caller.
        """
        try:
            definition = self.get_definition(action)
        except (KeyError, ValueError) as exc:
            return ActionExecutionResult(
                action=action,
                success=False,
                executed=False,
                approval_required=False,
                approval_granted=approval_granted,
                message="Action is not registered.",
                error=str(exc),
            )

        approval_required = definition.requires_approval

        allowed, reason = self.can_execute(
            action,
            approval_granted=approval_granted,
        )

        if not allowed:
            return ActionExecutionResult(
                action=action,
                success=False,
                executed=False,
                approval_required=approval_required,
                approval_granted=approval_granted,
                message=reason,
                error=reason,
            )

        handler = definition.handler
        if handler is None:
            # Defensive check; can_execute already catches this.
            return ActionExecutionResult(
                action=action,
                success=False,
                executed=False,
                approval_required=approval_required,
                approval_granted=approval_granted,
                message="Action has no registered handler.",
                error="missing_handler",
            )

        try:
            result = handler(payload or {})

            return ActionExecutionResult(
                action=action,
                success=True,
                executed=True,
                approval_required=approval_required,
                approval_granted=approval_granted,
                message=f"Action '{action}' executed successfully.",
                result=result,
            )
        except Exception as exc:
            return ActionExecutionResult(
                action=action,
                success=False,
                executed=False,
                approval_required=approval_required,
                approval_granted=approval_granted,
                message=f"Action '{action}' failed during execution.",
                error=str(exc),
            )

    def execute_if_authorized(
        self,
        action: str,
        payload: Mapping[str, Any] | None = None,
        *,
        approval_granted: bool = False,
    ) -> ActionExecutionResult:
        """
        Explicit convenience wrapper for agent nodes.

        This method does not bypass approval. It simply exposes the same
        guarded execution path with a semantic name for orchestration code.
        """
        return self.execute(
            action,
            payload,
            approval_granted=approval_granted,
        )