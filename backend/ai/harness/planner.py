import json
from typing import Protocol

from ai.harness.actions import AnswerAction, PlannerAction, parse_action
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
    fallback_answer: str | None = None,
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

    if fallback_answer is not None and _can_use_fallback(last_error):
        return AnswerAction(type="answer", answer=fallback_answer)

    raise PlannerInvalidAction(
        f"planner output invalid after {max_repair_attempts} repair attempt(s): {last_error}"
    ) from last_error


def _context_with_repair_message(
    context: CompiledContext,
    raw_output: str,
    error: Exception,
) -> CompiledContext:
    preview = _preview(raw_output)
    repair_message = _repair_message_for_error(error, preview)
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


def _can_use_fallback(error: Exception | None) -> bool:
    return error is not None and "markdown is not allowed" in str(error)


def _repair_message_for_error(error: Exception, preview: str) -> str:
    if _can_use_fallback(error):
        return (
            "上一次规划器输出是合法的 JSON，但 answer 字段使用了 Markdown 语法。\n"
            f"错误：{error}\n"
            f"上一次输出预览：{preview}\n"
            "请返回一个修正后的 JSON 对象。继续完成用户的请求，但把 answer 字段"
            "改写为纯对话文本。不要使用 Markdown 标题、无序列表、有序列表、加粗或斜体标记、"
            "代码块、引用块、表格或 Markdown 链接。如果用户要求输出或讲解 Markdown，"
            "请用纯文本说明，不要给出 Markdown 语法示例。"
        )
    return (
        "上一次规划器输出违反了规划器 JSON 契约。\n"
        f"错误：{error}\n"
        f"上一次输出预览：{preview}\n"
        "请返回一个修正后的 JSON 对象。不要包含 markdown、解释性文字或多余的字段。"
    )
