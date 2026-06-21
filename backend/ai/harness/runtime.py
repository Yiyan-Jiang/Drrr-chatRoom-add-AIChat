from __future__ import annotations

from dataclasses import asdict
from time import monotonic

from ai.harness.actions import (
    AnswerAction,
    AskUserAction,
    CompleteAction,
    DenyAction,
    ToolCallsAction,
    UpdateCheckpointAction,
)
from ai.harness.contracts import was_same_tool_call_repeated_without_progress
from ai.harness.context import compile_context
from ai.harness.errors import (
    CheckpointContractError,
    HarnessError,
    PlannerExceededMaxIterations,
    PlannerNoProgress,
)
from ai.harness.permissions import EffectivePolicy, PermissionDecision, check_permission
from ai.harness.planner import DeterministicAnswerPlanner, Planner, plan_with_repair
from ai.harness.planner_verifier import first_markdown_violation
from ai.repositories.harness_repository import SqlAlchemyHarnessRepository
from ai.runtime.default_tools import create_default_tool_registry
from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext


class HarnessRuntime:
    def __init__(
        self,
        repository=None,
        planner: Planner | None = None,
        registry: ToolRegistry | None = None,
        policy: EffectivePolicy | None = None,
        max_iterations: int = 8,
        planner_verifier=None,
        response_renderer=None,
        max_repair_attempts: int = 1,
    ):
        self._repository = repository or SqlAlchemyHarnessRepository()
        self._planner = planner or DeterministicAnswerPlanner()
        self._response_renderer = response_renderer
        self._registry = registry or create_default_tool_registry()
        self._policy = policy or EffectivePolicy(allowed_tools=self._registry.list_names())
        self._max_iterations = max_iterations
        self._planner_verifier = planner_verifier
        self._max_repair_attempts = max_repair_attempts

    async def run_turn(self, workspace) -> RunResult:
        run = await self._repository.load_or_create_run(workspace)

        try:
            for _iteration in range(self._max_iterations):
                events = await self._repository.list_events(run.run_id)
                artifacts = await self._repository.list_artifacts(run.run_id)
                context = compile_context(
                    workspace=workspace,
                    run=run,
                    events=events,
                    artifacts=artifacts,
                    registry=self._registry,
                    policy=_effective_policy_for_run(self._policy, run),
                )
                await self._repository.append_event(
                    run.run_id,
                    "context_compiled",
                    {
                        "ledger": [asdict(item) for item in context.ledger],
                        "token_estimate": context.token_estimate,
                    },
                )

                action = await plan_with_repair(
                    self._planner,
                    context,
                    verifier=self._planner_verifier,
                    registry=self._registry,
                    policy=_effective_policy_for_run(self._policy, run),
                    max_repair_attempts=self._max_repair_attempts,
                    on_repair_attempt=lambda payload: self._repository.append_event(
                        run.run_id,
                        "contract_rejected",
                        payload,
                    ),
                    fallback_answer=(
                        "我可以用普通文字继续说明，但不能用 Markdown 格式输出。"
                    ),
                )
                await self._repository.append_event(
                    run.run_id,
                    "planner_action",
                    _action_payload(action),
                )

                if isinstance(action, UpdateCheckpointAction):
                    _validate_checkpoint_contract(run, action.checkpoint)
                    run = await self._repository.update_checkpoint(run, action.checkpoint)
                    await self._repository.append_event(
                        run.run_id,
                        "checkpoint_updated",
                        {"checkpoint": action.checkpoint},
                    )
                    continue

                if isinstance(action, ToolCallsAction):
                    run_result = await self._execute_tool_calls(
                        run=run,
                        workspace=workspace,
                        action=action,
                        events=events,
                    )
                    if run_result is not None:
                        return run_result
                    continue

                if isinstance(action, AnswerAction):
                    from ai.orchestrator.schemas import RunResult

                    answer = await self._render_terminal_answer(workspace, action.answer)
                    await self._repository.append_event(
                        run.run_id,
                        "answer",
                        {"answer": answer},
                    )
                    run = await self._repository.mark_terminal(run, "completed")
                    return RunResult(
                        answer=answer,
                        trace_id=run.run_id,
                        metadata={"runtime": "harness", "status": "completed"},
                    )

                if isinstance(action, CompleteAction):
                    from ai.orchestrator.schemas import RunResult

                    answer = await self._render_terminal_answer(workspace, action.answer)
                    await self._repository.append_event(
                        run.run_id,
                        "complete",
                        {"answer": answer, "final_state": action.final_state},
                    )
                    await self._repository.write_artifact(
                        run,
                        "run_final_state",
                        action.final_state,
                        request_id=workspace.command.request_id,
                    )
                    run = await self._repository.mark_terminal(run, "completed")
                    return RunResult(
                        answer=answer,
                        trace_id=run.run_id,
                        metadata={"runtime": "harness", "status": "completed"},
                    )

                if isinstance(action, AskUserAction):
                    from ai.orchestrator.schemas import RunResult

                    question = await self._render_terminal_answer(workspace, action.question)
                    await self._repository.append_event(
                        run.run_id,
                        "ask_user",
                        {"question": question},
                    )
                    run = await self._repository.mark_terminal(run, "waiting_user")
                    return RunResult(
                        answer=question,
                        trace_id=run.run_id,
                        metadata={"runtime": "harness", "status": "waiting_user"},
                    )

                if isinstance(action, DenyAction):
                    from ai.orchestrator.schemas import RunResult

                    reason = await self._render_terminal_answer(workspace, action.reason)
                    await self._repository.append_event(
                        run.run_id,
                        "deny",
                        {"reason": reason},
                    )
                    run = await self._repository.mark_terminal(run, "blocked")
                    return RunResult(
                        answer=reason,
                        trace_id=run.run_id,
                        metadata={"runtime": "harness", "status": "blocked"},
                    )

            raise PlannerExceededMaxIterations("planner exceeded max iterations")
        except HarnessError as exc:
            await self._repository.mark_failed(run, exc.error_code, str(exc))
            raise

    async def _execute_tool_calls(
        self,
        run,
        workspace,
        action: ToolCallsAction,
        events: list,
    ):
        from ai.orchestrator.schemas import RunResult

        for call in action.tool_calls:
            if was_same_tool_call_repeated_without_progress(call, events):
                raise PlannerNoProgress(f"repeated tool call without progress: {call.name}")

            tool = self._registry.get(call.name)
            arguments = tool.normalize(call.arguments)
            await self._repository.append_event(
                run.run_id,
                "tool_call_requested",
                {"call_id": call.id, "tool": call.name, "arguments": arguments},
            )

            decision = check_permission(
                tool,
                arguments,
                _effective_policy_for_run(self._policy, run),
                workspace,
            )
            await self._repository.append_event(
                run.run_id,
                "permission_decision",
                {
                    "call_id": call.id,
                    "tool": call.name,
                    "decision": asdict(decision),
                },
            )

            if decision.kind == "deny":
                run = await self._repository.mark_terminal(run, "blocked")
                return RunResult(
                    answer=decision.reason,
                    trace_id=run.run_id,
                    metadata={"runtime": "harness", "status": "blocked"},
                )

            if decision.kind == "ask":
                run = await self._repository.mark_terminal(run, "waiting_permission")
                return RunResult(
                    answer=decision.reason,
                    trace_id=run.run_id,
                    metadata={
                        "runtime": "harness",
                        "status": "waiting_permission",
                        "permission_request": asdict(decision),
                    },
                )

            started = monotonic()
            try:
                result = await tool.execute(
                    ToolExecutionContext(
                        run_id=run.run_id,
                        session_id=workspace.session.session_id,
                        user_id=workspace.command.user_id,
                        call_id=call.id,
                        workspace_id=(workspace.command.metadata or {}).get("workspace_id"),
                        checkpoint_payload=getattr(run, "checkpoint_payload", None),
                        run=run,
                        repository=self._repository,
                        tool_registry=self._registry,
                    ),
                    arguments,
                )
            except Exception as exc:
                result = ToolResult(
                    tool_name=tool.name,
                    call_id=call.id,
                    ok=False,
                    result_kind="error",
                    preview=str(exc),
                    payload={},
                    facts=[],
                    error_code=type(exc).__name__,
                    error_message=str(exc),
                )

            result_payload = asdict(result)
            result_payload["elapsed_ms"] = int((monotonic() - started) * 1000)
            await self._repository.append_event(
                run.run_id,
                "tool_result",
                {
                    "call_id": call.id,
                    "tool": tool.name,
                    "arguments": arguments,
                    "result": result_payload,
                },
            )

        return None

    async def _render_terminal_answer(self, workspace, draft_text: str) -> str:
        if self._response_renderer is None:
            return draft_text
        rendered = await self._response_renderer.render(
            character=getattr(workspace.command, "character", None),
            draft_text=draft_text,
        )
        if first_markdown_violation(rendered) is not None:
            return draft_text
        return rendered


def _action_payload(action) -> dict:
    if hasattr(action, "model_dump"):
        return action.model_dump()
    return action.dict()


def _effective_policy_for_run(base_policy: EffectivePolicy, run) -> EffectivePolicy:
    skill_state = getattr(run, "skill_state_payload", None) or {}
    skill_policy = skill_state.get("effective_policy") or {}
    denied_tools = set(base_policy.denied_tools or [])
    denied_tools.update(skill_policy.get("deny") or [])
    ask_tools = set(base_policy.ask_tools or [])
    ask_tools.update(skill_policy.get("ask") or [])
    allowed_tools = set(base_policy.allowed_tools)
    allowed_tools.update(skill_policy.get("allow") or [])
    allowed_tools.update(skill_state.get("effective_tools") or [])

    return EffectivePolicy(
        allowed_tools=sorted(allowed_tools),
        ask_tools=sorted(ask_tools),
        denied_tools=sorted(denied_tools),
    )


def _validate_checkpoint_contract(run, checkpoint: dict) -> None:
    skill_state = getattr(run, "skill_state_payload", None) or {}
    schema = skill_state.get("effective_checkpoint_schema") or {}
    required_keys = schema.get("required") or []
    missing = [key for key in required_keys if key not in checkpoint]
    if missing:
        raise CheckpointContractError(
            f"checkpoint missing required key(s): {', '.join(missing)}"
        )
