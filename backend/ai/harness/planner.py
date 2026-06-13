import json
from typing import Protocol

from ai.harness.actions import PlannerAction, parse_action
from ai.harness.context import CompiledContext
from ai.harness.errors import (
    ActionParseError,
    PlannerContractError,
    PlannerInvalidAction,
)


class Planner(Protocol):
    async def plan(self, context: CompiledContext) -> str:
        ...


class DeterministicAnswerPlanner:
    async def plan(self, context: CompiledContext) -> str:
        current_input = ""
        for message in reversed(context.messages):
            if message.get("role") == "user":
                current_input = message.get("content", "")
                break
        return json.dumps({"type": "answer", "answer": current_input}, ensure_ascii=False)


async def plan_with_repair(
    planner: Planner,
    context: CompiledContext,
    *,
    verifier=None,
    registry=None,
    policy=None,
    max_repair_attempts: int = 1,
    on_repair_attempt=None,
) -> PlannerAction:
    current_context = context
    last_error: Exception | None = None

    for attempt in range(max_repair_attempts + 1):
        raw = await planner.plan(current_context)
        try:
            action = parse_action(raw)
            if verifier is not None:
                if registry is None or policy is None:
                    raise PlannerContractError(
                        "planner verifier requires registry and policy"
                    )
                action = verifier.verify(action, registry=registry, policy=policy)
            return action
        except (ActionParseError, PlannerContractError) as exc:
            last_error = exc
            if on_repair_attempt is not None:
                await on_repair_attempt(
                    {
                        "attempt": attempt,
                        "error_code": getattr(exc, "error_code", type(exc).__name__),
                        "error_message": str(exc),
                        "raw_output_preview": _preview(raw),
                    }
                )
            if attempt >= max_repair_attempts:
                break
            current_context = _context_with_repair_message(
                context=current_context,
                raw_output=raw,
                error=exc,
            )

    raise PlannerInvalidAction(
        f"planner output invalid after {max_repair_attempts} repair attempt(s): {last_error}"
    ) from last_error


def _context_with_repair_message(
    context: CompiledContext,
    raw_output: str,
    error: Exception,
) -> CompiledContext:
    preview = _preview(raw_output)
    repair_message = (
        "The previous planner output violated the planner JSON contract.\n"
        f"Error: {error}\n"
        f"Previous output preview: {preview}\n"
        "Return one corrected JSON object. Do not include markdown, prose, or extra keys."
    )
    return CompiledContext(
        messages=[
            *context.messages,
            {"role": "system", "content": repair_message},
        ],
        ledger=context.ledger,
        token_estimate=context.token_estimate + max(1, len(repair_message) // 4),
    )


def _preview(raw_output: str) -> str:
    return raw_output if len(raw_output) <= 500 else raw_output[:497] + "..."
