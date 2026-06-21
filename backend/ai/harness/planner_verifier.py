import re

from ai.harness.actions import AnswerAction, PlannerAction, ToolCallsAction
from ai.harness.errors import PlannerContractError
from ai.harness.permissions import EffectivePolicy
from ai.harness.planner_schema import LLM_PLANNER_ALLOWED_ACTIONS
from ai.runtime.registry import ToolRegistry, UnknownTool
from ai.runtime.schema_validation import ToolSchemaValidationError


class PlannerVerifier:
    def __init__(self, allowed_actions: list[str] | None = None):
        self._allowed_actions = set(allowed_actions or LLM_PLANNER_ALLOWED_ACTIONS)

    def verify(
        self,
        action: PlannerAction,
        registry: ToolRegistry,
        policy: EffectivePolicy,
    ) -> PlannerAction:
        action_type = getattr(action, "type", None)
        if action_type not in self._allowed_actions:
            raise PlannerContractError(f"action type not allowed: {action_type}")

        if isinstance(action, AnswerAction):
            self._verify_answer(action)

        if isinstance(action, ToolCallsAction):
            self._verify_tool_calls(action, registry, policy)

        return action

    def _verify_answer(self, action: AnswerAction) -> None:
        violation = first_markdown_violation(action.answer)
        if violation is not None:
            raise PlannerContractError(
                f"markdown is not allowed in answer: {violation}"
            )

    def _verify_tool_calls(
        self,
        action: ToolCallsAction,
        registry: ToolRegistry,
        policy: EffectivePolicy,
    ) -> None:
        allowed_tools = set(policy.allowed_tools)
        denied_tools = set(policy.denied_tools or [])

        for index, call in enumerate(action.tool_calls):
            try:
                tool = registry.get(call.name)
            except UnknownTool as exc:
                raise PlannerContractError(
                    f"tool_calls[{index}].name tool not registered: {call.name}"
                ) from exc

            if call.name in denied_tools or call.name not in allowed_tools:
                raise PlannerContractError(
                    f"tool_calls[{index}].name tool not allowed by policy: {call.name}"
                )

            try:
                tool.validate_arguments(call.arguments)
            except ToolSchemaValidationError as exc:
                raise PlannerContractError(
                    f"tool_calls[{index}].arguments {exc}"
                ) from exc


def first_markdown_violation(answer: str) -> str | None:
    patterns = [
        ("fenced code block", re.compile(r"```")),
        ("heading", re.compile(r"(?m)^\s{0,3}#{1,6}\s+\S")),
        ("unordered list", re.compile(r"(?m)^\s*[-*+]\s+\S")),
        ("ordered list", re.compile(r"(?m)^\s*\d+[.)]\s+\S")),
        ("blockquote", re.compile(r"(?m)^\s*>\s+\S")),
        ("table", re.compile(r"(?m)^\s*\|.+\|\s*$")),
        ("bold emphasis", re.compile(r"(\*\*|__)\S.*?(\*\*|__)")),
        ("markdown link", re.compile(r"\[[^\]]+\]\([^)]+\)")),
    ]
    for label, pattern in patterns:
        if pattern.search(answer):
            return label
    return None
