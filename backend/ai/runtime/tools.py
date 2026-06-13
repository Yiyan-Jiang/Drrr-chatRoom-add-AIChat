from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from ai.runtime.results import ToolResult
from ai.runtime.schema_validation import validate_tool_arguments


@dataclass(frozen=True)
class ToolPermission:
    scope: str
    requires_user_approval: bool = False


@dataclass(frozen=True)
class ToolExecutionContext:
    run_id: str
    session_id: str
    user_id: int
    call_id: str
    workspace_id: str | None = None
    checkpoint_payload: dict | None = None
    run: Any | None = None
    repository: Any | None = None
    tool_registry: Any | None = None


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict
    permission: ToolPermission
    normalize: Callable[[dict], dict]
    execute: Callable[[ToolExecutionContext, dict], Awaitable[ToolResult]]
    when_to_use: str = ""

    def validate_arguments(self, arguments: dict) -> None:
        validate_tool_arguments(self.input_schema, arguments)
