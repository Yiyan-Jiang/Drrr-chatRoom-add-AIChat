from dataclasses import dataclass
from typing import Literal

from ai.runtime.tools import ToolSpec


@dataclass(frozen=True)
class EffectivePolicy:
    allowed_tools: list[str]
    ask_tools: list[str] | None = None
    denied_tools: list[str] | None = None


@dataclass(frozen=True)
class PermissionDecision:
    kind: Literal["allow", "ask", "deny"]
    reason: str
    required_scope: str | None = None
    resource_id: str | None = None


def check_permission(
    tool: ToolSpec,
    arguments: dict,
    policy: EffectivePolicy,
    workspace,
) -> PermissionDecision:
    denied_tools = set(policy.denied_tools or [])
    ask_tools = set(policy.ask_tools or [])
    allowed_tools = set(policy.allowed_tools)

    if tool.name in denied_tools:
        return PermissionDecision(kind="deny", reason=f"tool denied by policy: {tool.name}")

    if tool.name in ask_tools:
        return PermissionDecision(
            kind="ask",
            reason="tool requires policy approval",
            required_scope=tool.permission.scope,
            resource_id=arguments.get("resource_id"),
        )

    if tool.name not in allowed_tools:
        return PermissionDecision(kind="deny", reason=f"tool not allowed: {tool.name}")

    if tool.permission.requires_user_approval:
        return PermissionDecision(
            kind="ask",
            reason="tool requires user approval",
            required_scope=tool.permission.scope,
            resource_id=arguments.get("resource_id"),
        )

    return PermissionDecision(kind="allow", reason="allowed")
