"""
Agent-facing action tools.

These wrappers expose the action execution layer to agent nodes without
allowing the agent to bypass registry and approval controls.
"""

from __future__ import annotations

from typing import Any, Mapping

from backend.actions.executor import ActionExecutionResult, ActionExecutor
from backend.actions.registry import ActionRegistry, create_default_action_registry


class ActionTools:
    """Collection of guarded action operations available to the agent."""

    def __init__(
        self,
        executor: ActionExecutor | None = None,
        registry: ActionRegistry | None = None,
    ) -> None:
        if executor is not None:
            self.executor = executor
        else:
            self.executor = ActionExecutor(
                registry or create_default_action_registry()
            )

    def available_actions(self) -> list[str]:
        """Return identifiers of registered actions."""
        return self.executor.registry.ids()

    def validate_action(
        self,
        action: str,
        *,
        approval_granted: bool = False,
    ) -> dict[str, Any]:
        """Check whether an action can currently be executed."""
        allowed, reason = self.executor.can_execute(
            action,
            approval_granted=approval_granted,
        )

        return {
            "action": action,
            "allowed": allowed,
            "approval_granted": approval_granted,
            "reason": reason,
        }

    def execute(
        self,
        action: str,
        payload: Mapping[str, Any] | None = None,
        *,
        approval_granted: bool = False,
    ) -> ActionExecutionResult:
        """
        Execute an action through the guarded ActionExecutor.

        No direct handler invocation is permitted here.
        """
        return self.executor.execute(
            action,
            payload,
            approval_granted=approval_granted,
        )


def create_action_tools(
    *,
    registry: ActionRegistry | None = None,
) -> ActionTools:
    """Create the default action-tool collection."""
    return ActionTools(
        registry=registry or create_default_action_registry(),
    )