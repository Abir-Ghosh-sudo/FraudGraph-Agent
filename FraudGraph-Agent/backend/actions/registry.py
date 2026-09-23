from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


@dataclass(slots=True)
class ActionDefinition:
    """Metadata and handler definition for an executable action."""

    name: str
    description: str
    handler: Callable[..., Any] | None = None
    requires_approval: bool = True
    allowed_roles: set[str] = field(default_factory=set)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_execute(self, role: str | None = None) -> bool:
        if not self.enabled:
            return False

        if not self.allowed_roles:
            return True

        if role is None:
            return False

        return role in self.allowed_roles


class ActionRegistry:
    """
    Central registry for actions available to the fraud investigation agent.

    Registration is separate from execution. This allows policy and approval
    checks to remain in the action executor instead of letting the agent
    directly invoke arbitrary functions.
    """

    def __init__(
        self,
        actions: Iterable[ActionDefinition] | None = None,
    ) -> None:
        self._actions: dict[str, ActionDefinition] = {}

        for action in actions or []:
            self.register(action)

    def register(
        self,
        action: ActionDefinition | Mapping[str, Any],
        *,
        replace: bool = False,
    ) -> ActionDefinition:
        """Register an action definition."""

        definition = self._normalize(action)

        if (
            definition.name in self._actions
            and not replace
        ):
            raise ValueError(
                f"Action already registered: {definition.name}"
            )

        self._actions[definition.name] = definition
        return definition

    def unregister(self, name: str) -> ActionDefinition | None:
        """Remove an action and return its previous definition."""

        return self._actions.pop(name, None)

    def get(self, name: str) -> ActionDefinition | None:
        """Return an action if registered."""

        return self._actions.get(name)

    def require(self, name: str) -> ActionDefinition:
        """Return an action or raise a clear lookup error."""

        action = self.get(name)

        if action is None:
            raise KeyError(
                f"Unknown action: {name}"
            )

        return action

    def exists(self, name: str) -> bool:
        return name in self._actions

    def names(self) -> list[str]:
        return sorted(self._actions)

    def values(self) -> list[ActionDefinition]:
        return list(self._actions.values())

    def items(self) -> list[tuple[str, ActionDefinition]]:
        return list(self._actions.items())

    def enabled(self) -> list[ActionDefinition]:
        return [
            action
            for action in self._actions.values()
            if action.enabled
        ]

    def executable(
        self,
        *,
        role: str | None = None,
    ) -> list[ActionDefinition]:
        """Return enabled actions executable by the supplied role."""

        return [
            action
            for action in self._actions.values()
            if action.can_execute(role)
        ]

    def set_enabled(
        self,
        name: str,
        enabled: bool,
    ) -> ActionDefinition:
        """Enable or disable an existing action."""

        action = self.require(name)
        action.enabled = bool(enabled)
        return action

    def clear(self) -> None:
        self._actions.clear()

    def __contains__(self, name: str) -> bool:
        return self.exists(name)

    def __len__(self) -> int:
        return len(self._actions)

    @staticmethod
    def _normalize(
        action: ActionDefinition | Mapping[str, Any],
    ) -> ActionDefinition:
        if isinstance(action, ActionDefinition):
            return action

        if not isinstance(action, Mapping):
            raise TypeError(
                "action must be ActionDefinition or mapping"
            )

        name = action.get("name")

        if not name:
            raise ValueError(
                "Action definition requires a name"
            )

        allowed_roles = action.get(
            "allowed_roles",
            set(),
        )

        if isinstance(allowed_roles, str):
            allowed_roles = {allowed_roles}
        else:
            allowed_roles = set(allowed_roles or [])

        metadata = action.get("metadata", {})

        if not isinstance(metadata, Mapping):
            metadata = {}

        return ActionDefinition(
            name=str(name),
            description=str(
                action.get("description", "")
            ),
            handler=action.get("handler"),
            requires_approval=bool(
                action.get("requires_approval", True)
            ),
            allowed_roles=allowed_roles,
            enabled=bool(
                action.get("enabled", True)
            ),
            metadata=dict(metadata),
        )


def create_default_action_registry() -> ActionRegistry:
    """
    Create the standard HHGOA action registry.

    Handlers are intentionally left unset here. Concrete integrations are
    registered by the action execution layer.
    """

    registry = ActionRegistry()

    registry.register(
        ActionDefinition(
            name="allow_transaction",
            description="Allow a previously flagged transaction.",
            requires_approval=True,
        )
    )

    registry.register(
        ActionDefinition(
            name="block_transaction",
            description="Block a suspicious transaction.",
            requires_approval=True,
        )
    )

    registry.register(
        ActionDefinition(
            name="monitor_account",
            description="Place an account under enhanced monitoring.",
            requires_approval=True,
        )
    )

    registry.register(
        ActionDefinition(
            name="block_account",
            description="Restrict an account according to policy.",
            requires_approval=True,
        )
    )

    registry.register(
        ActionDefinition(
            name="warn_customer",
            description="Send a customer fraud warning.",
            requires_approval=True,
        )
    )

    registry.register(
        ActionDefinition(
            name="create_case",
            description="Create or update a fraud investigation case.",
            requires_approval=False,
        )
    )

    registry.register(
        ActionDefinition(
            name="request_evidence",
            description="Request additional approved evidence.",
            requires_approval=False,
        )
    )

    registry.register(
        ActionDefinition(
            name="escalate",
            description="Escalate the investigation to an authorized analyst.",
            requires_approval=False,
        )
    )

    registry.register(
        ActionDefinition(
            name="file_sar",
            description="Prepare a suspicious activity report for filing.",
            requires_approval=True,
        )
    )

    return registry