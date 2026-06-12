import unittest
from dataclasses import dataclass
from datetime import datetime


class HarnessActionParserTest(unittest.TestCase):
    def test_parse_answer_action_from_json(self):
        from ai.harness.actions import AnswerAction, parse_action

        action = parse_action('{"type": "answer", "answer": "hello"}')

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, "hello")

    def test_parse_answer_action_from_model_json_without_type(self):
        from ai.harness.actions import AnswerAction, parse_action

        action = parse_action('{"answer": "hello"}')

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, "hello")

    def test_parse_action_extracts_json_from_surrounding_text(self):
        from ai.harness.actions import AnswerAction, parse_action

        action = parse_action('I will answer now: {"type": "answer", "answer": "hello"}')

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, "hello")

    def test_tool_calls_requires_at_least_one_call(self):
        from ai.harness.actions import parse_action
        from ai.harness.errors import ActionParseError

        with self.assertRaises(ActionParseError):
            parse_action('{"type": "tool_calls", "tool_calls": []}')

    def test_parse_all_runtime_action_types(self):
        from ai.harness.actions import (
            AskUserAction,
            CompleteAction,
            DenyAction,
            ToolCallsAction,
            UpdateCheckpointAction,
            parse_action,
        )

        self.assertIsInstance(
            parse_action('{"type": "ask_user", "question": "Need more?"}'),
            AskUserAction,
        )
        self.assertIsInstance(
            parse_action(
                '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "demo", "arguments": {}}]}'
            ),
            ToolCallsAction,
        )
        self.assertIsInstance(
            parse_action('{"type": "update_checkpoint", "checkpoint": {"step": "one"}}'),
            UpdateCheckpointAction,
        )
        self.assertIsInstance(
            parse_action(
                '{"type": "complete", "answer": "done", "final_state": {"ok": true}}'
            ),
            CompleteAction,
        )
        self.assertIsInstance(
            parse_action('{"type": "deny", "reason": "not allowed"}'),
            DenyAction,
        )

    def test_parse_action_rejects_unknown_or_non_json_output(self):
        from ai.harness.actions import parse_action
        from ai.harness.errors import ActionParseError

        with self.assertRaises(ActionParseError):
            parse_action('{"type": "missing"}')

        with self.assertRaises(ActionParseError):
            parse_action("plain text answer")


class HarnessPlannerRepairTest(unittest.IsolatedAsyncioTestCase):
    async def test_plan_with_repair_retries_once_after_invalid_output(self):
        from ai.harness.actions import AnswerAction
        from ai.harness.context import CompiledContext
        from ai.harness.planner import plan_with_repair

        class FakePlanner:
            def __init__(self):
                self.outputs = [
                    "not json",
                    '{"type": "answer", "answer": "fixed"}',
                ]
                self.calls = []

            async def plan(self, context):
                self.calls.append(context)
                return self.outputs.pop(0)

        planner = FakePlanner()
        context = CompiledContext(messages=[], ledger=[], token_estimate=0)

        action = await plan_with_repair(planner, context)

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, "fixed")
        self.assertEqual(len(planner.calls), 2)

    async def test_deterministic_planner_escapes_user_input_as_json(self):
        from ai.harness.actions import AnswerAction, parse_action
        from ai.harness.context import CompiledContext
        from ai.harness.planner import DeterministicAnswerPlanner

        context = CompiledContext(
            messages=[{"role": "user", "content": 'say "hello"'}],
            ledger=[],
            token_estimate=0,
        )

        raw = await DeterministicAnswerPlanner().plan(context)
        action = parse_action(raw)

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, 'say "hello"')


class FakeScalarResult:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records


class FakeExecuteResult:
    def __init__(self, records):
        self._records = records

    def scalar_one_or_none(self):
        return self._records[0] if self._records else None

    def scalars(self):
        return FakeScalarResult(self._records)


class FakeSession:
    def __init__(self, records=None):
        self.records = records or []
        self.added = []
        self.flushes = 0

    def add(self, record):
        self.added.append(record)
        self.records.append(record)

    async def execute(self, _statement):
        return FakeExecuteResult(list(self.records))

    async def flush(self):
        self.flushes += 1


class HarnessRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_append_event_assigns_next_sequence_number(self):
        from ai.models.harness_event import HarnessEvent
        from ai.repositories.harness_repository import append_harness_event

        session = FakeSession(
            records=[
                HarnessEvent(
                    run_id="run-1",
                    sequence_no=1,
                    event_type="context_compiled",
                    payload={},
                )
            ]
        )

        event = await append_harness_event(
            session,
            run_id="run-1",
            event_type="answer",
            payload={"answer": "hello"},
            now=datetime(2026, 5, 26, 12, 0, 0),
        )

        self.assertEqual(event.sequence_no, 2)
        self.assertEqual(event.event_type, "answer")
        self.assertEqual(session.flushes, 1)

    async def test_update_run_checkpoint_flushes_without_committing(self):
        from ai.models.harness_run import HarnessRun
        from ai.repositories.harness_repository import update_run_checkpoint

        run = HarnessRun(run_id="run-1", user_id=7, status="running")
        session = FakeSession(records=[run])

        updated = await update_run_checkpoint(
            session,
            run,
            checkpoint={"step": "waiting"},
            now=datetime(2026, 5, 26, 12, 0, 0),
        )

        self.assertIs(updated, run)
        self.assertEqual(run.checkpoint_payload, {"step": "waiting"})
        self.assertEqual(session.flushes, 1)


@dataclass
class FakeCommand:
    request_id: str = "request-1"
    session_id: str | None = "session-1"
    user_id: int = 7
    message: str = "hello"
    character: str | None = None
    metadata: dict | None = None


@dataclass
class FakeWorkspace:
    command: FakeCommand
    session: object
    recent_turns: list


class HarnessContextTest(unittest.TestCase):
    def test_compile_context_includes_current_input_and_ledger(self):
        from ai.harness.context import compile_context

        session = type("Session", (), {"session_id": "session-1", "user_id": 7})()
        run = type("Run", (), {"run_id": "run-1", "checkpoint_payload": {"step": "one"}})()
        workspace = FakeWorkspace(
            command=FakeCommand(message="summarize this"),
            session=session,
            recent_turns=[],
        )

        context = compile_context(workspace=workspace, run=run, events=[], artifacts=[])

        self.assertTrue(any(message["content"] == "summarize this" for message in context.messages))
        self.assertIn("current_input", [item.section for item in context.ledger])
        self.assertGreater(context.token_estimate, 0)


class FakeHarnessRepository:
    def __init__(self):
        self.run = type(
            "Run",
            (),
            {
                "run_id": "run-1",
                "session_id": "session-1",
                "request_id": "request-1",
                "user_id": 7,
                "status": "created",
                "checkpoint_payload": None,
            },
        )()
        self.events = []
        self.artifacts = []

    async def load_or_create_run(self, workspace):
        return self.run

    async def list_events(self, run_id):
        return list(self.events)

    async def list_artifacts(self, run_id):
        return list(self.artifacts)

    async def append_event(self, run_id, event_type, payload):
        event = type(
            "Event",
            (),
            {
                "run_id": run_id,
                "sequence_no": len(self.events) + 1,
                "event_type": event_type,
                "payload": payload,
            },
        )()
        self.events.append(event)
        return event

    async def update_checkpoint(self, run, checkpoint):
        run.checkpoint_payload = checkpoint
        return run

    async def mark_terminal(self, run, status):
        run.status = status
        return run

    async def mark_failed(self, run, error_code, error_message):
        run.status = "failed"
        run.error_code = error_code
        run.error_message = error_message
        return run

    async def write_artifact(
        self,
        run,
        artifact_type,
        payload,
        request_id=None,
    ):
        artifact = type(
            "Artifact",
            (),
            {
                "run_id": run.run_id,
                "session_id": run.session_id,
                "request_id": request_id or run.request_id,
                "user_id": run.user_id,
                "artifact_type": artifact_type,
                "payload": payload,
            },
        )()
        self.artifacts.append(artifact)
        await self.append_event(
            run.run_id,
            "artifact_written",
            {"artifact_type": artifact_type, "payload": payload},
        )
        return artifact


class QueuePlanner:
    def __init__(self, outputs):
        self.outputs = list(outputs)

    async def plan(self, _context):
        return self.outputs.pop(0)


class HarnessRuntimeTest(unittest.IsolatedAsyncioTestCase):
    async def test_runtime_answer_action_records_events_and_returns_result(self):
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(['{"type": "answer", "answer": "hello"}']),
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        result = await runtime.run_turn(workspace)

        self.assertEqual(result.answer, "hello")
        self.assertEqual(result.trace_id, "run-1")
        self.assertIn("context_compiled", [event.event_type for event in repository.events])
        self.assertIn("planner_action", [event.event_type for event in repository.events])
        self.assertIn("answer", [event.event_type for event in repository.events])

    async def test_runtime_update_checkpoint_then_answer(self):
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "update_checkpoint", "checkpoint": {"step": "waiting"}}',
                    '{"type": "answer", "answer": "recorded"}',
                ]
            ),
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        result = await runtime.run_turn(workspace)

        self.assertEqual(result.answer, "recorded")
        self.assertEqual(repository.run.checkpoint_payload, {"step": "waiting"})
        self.assertIn("checkpoint_updated", [event.event_type for event in repository.events])

    async def test_runtime_stops_after_max_iterations(self):
        from ai.harness.errors import PlannerExceededMaxIterations
        from ai.harness.runtime import HarnessRuntime

        runtime = HarnessRuntime(
            repository=FakeHarnessRepository(),
            planner=QueuePlanner(
                [
                    '{"type": "update_checkpoint", "checkpoint": {"step": "one"}}',
                    '{"type": "update_checkpoint", "checkpoint": {"step": "two"}}',
                ]
            ),
            max_iterations=2,
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        with self.assertRaises(PlannerExceededMaxIterations):
            await runtime.run_turn(workspace)

    async def test_runtime_ask_user_returns_waiting_user_status(self):
        from ai.harness.runtime import HarnessRuntime

        runtime = HarnessRuntime(
            repository=FakeHarnessRepository(),
            planner=QueuePlanner(['{"type": "ask_user", "question": "Which topic?"}']),
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        result = await runtime.run_turn(workspace)

        self.assertEqual(result.answer, "Which topic?")
        self.assertEqual(result.metadata["status"], "waiting_user")

    async def test_runtime_deny_returns_blocked_status(self):
        from ai.harness.runtime import HarnessRuntime

        runtime = HarnessRuntime(
            repository=FakeHarnessRepository(),
            planner=QueuePlanner(['{"type": "deny", "reason": "not allowed"}']),
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        result = await runtime.run_turn(workspace)

        self.assertEqual(result.answer, "not allowed")
        self.assertEqual(result.metadata["status"], "blocked")

    async def test_runtime_complete_writes_final_artifact_and_returns_completed(self):
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "complete", "answer": "done", "final_state": {"score": 1}}']
            ),
        )
        workspace = FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

        result = await runtime.run_turn(workspace)

        self.assertEqual(result.answer, "done")
        self.assertEqual(result.metadata["status"], "completed")
        self.assertEqual(repository.artifacts[0].artifact_type, "run_final_state")
        self.assertEqual(repository.artifacts[0].payload, {"score": 1})


class RuntimeToolRegistryTest(unittest.IsolatedAsyncioTestCase):
    async def test_tool_registry_rejects_duplicate_and_unknown_tools(self):
        from ai.runtime.registry import ToolRegistry, UnknownTool
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            return ToolResult(
                tool_name="demo",
                call_id="call-1",
                ok=True,
                result_kind="demo",
                preview="done",
                payload={},
                facts=[],
            )

        spec = ToolSpec(
            name="demo",
            description="Demo tool",
            input_schema={},
            permission=ToolPermission(scope="read"),
            normalize=lambda arguments: arguments,
            execute=execute,
        )
        registry = ToolRegistry()
        registry.register(spec)

        self.assertIs(registry.get("demo"), spec)
        with self.assertRaises(ValueError):
            registry.register(spec)
        with self.assertRaises(UnknownTool):
            registry.get("missing")

    def test_default_tool_registry_exposes_minimal_runtime_tools(self):
        from ai.runtime.default_tools import create_default_tool_registry

        registry = create_default_tool_registry()

        self.assertIn("read_checkpoint", registry.list_names())
        self.assertIn("write_artifact", registry.list_names())
        self.assertIn("record_note", registry.list_names())


class HarnessPermissionTest(unittest.TestCase):
    def test_permission_denies_tool_not_in_allowed_tools(self):
        from ai.harness.permissions import EffectivePolicy, check_permission
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            raise AssertionError("should not execute")

        tool = ToolSpec(
            name="search",
            description="Search",
            input_schema={},
            permission=ToolPermission(scope="read"),
            normalize=lambda arguments: arguments,
            execute=execute,
        )

        decision = check_permission(
            tool=tool,
            arguments={},
            policy=EffectivePolicy(allowed_tools=[]),
            workspace=None,
        )

        self.assertEqual(decision.kind, "deny")
        self.assertIn("tool not allowed", decision.reason)

    def test_permission_asks_when_tool_requires_user_approval(self):
        from ai.harness.permissions import EffectivePolicy, check_permission
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            raise AssertionError("should not execute")

        tool = ToolSpec(
            name="write_resource",
            description="Write",
            input_schema={},
            permission=ToolPermission(scope="write", requires_user_approval=True),
            normalize=lambda arguments: arguments,
            execute=execute,
        )

        decision = check_permission(
            tool=tool,
            arguments={},
            policy=EffectivePolicy(allowed_tools=["write_resource"]),
            workspace=None,
        )

        self.assertEqual(decision.kind, "ask")
        self.assertEqual(decision.required_scope, "write")


class HarnessContractTest(unittest.TestCase):
    def test_repeated_tool_call_without_progress_is_detected(self):
        from ai.harness.actions import ToolCall
        from ai.harness.contracts import was_same_tool_call_repeated_without_progress

        events = [
            type(
                "Event",
                (),
                {
                    "event_type": "tool_result",
                    "payload": {"tool": "search", "arguments": {"query": "x"}},
                },
            )(),
            type(
                "Event",
                (),
                {
                    "event_type": "tool_result",
                    "payload": {"tool": "search", "arguments": {"query": "x"}},
                },
            )(),
        ]

        repeated = was_same_tool_call_repeated_without_progress(
            ToolCall(id="call-3", name="search", arguments={"query": "x"}),
            events,
        )

        self.assertTrue(repeated)


class ArtifactRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_write_artifact_persists_artifact_and_event(self):
        from ai.repositories.artifact_repository import write_artifact

        session = FakeSession()

        artifact = await write_artifact(
            session,
            run_id="run-1",
            session_id="session-1",
            request_id="request-1",
            user_id=7,
            artifact_type="response_refs",
            payload={"refs": []},
            now=datetime(2026, 5, 26, 12, 0, 0),
        )

        event_types = [record.event_type for record in session.records if hasattr(record, "event_type")]
        self.assertEqual(artifact.artifact_type, "response_refs")
        self.assertIn("artifact_written", event_types)
        self.assertEqual(session.flushes, 2)


class HarnessRuntimeToolCallsTest(unittest.IsolatedAsyncioTestCase):
    def _workspace(self):
        return FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

    async def test_runtime_blocks_denied_tool_call_and_records_permission_event(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            return ToolResult(
                tool_name="search",
                call_id="call-1",
                ok=True,
                result_kind="result",
                preview="done",
                payload={},
                facts=[],
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="search",
                description="Search",
                input_schema={},
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "search", "arguments": {"query": "x"}}]}']
            ),
            registry=registry,
            policy=EffectivePolicy(allowed_tools=[]),
        )

        result = await runtime.run_turn(self._workspace())

        self.assertEqual(result.metadata["status"], "blocked")
        self.assertIn("permission_decision", [event.event_type for event in repository.events])

    async def test_runtime_executes_allowed_tool_records_result_then_answers(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(context, arguments):
            return ToolResult(
                tool_name="search",
                call_id=context.call_id,
                ok=True,
                result_kind="result",
                preview=arguments["query"],
                payload={"items": [arguments["query"]]},
                facts=[],
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="search",
                description="Search",
                input_schema={},
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: {"query": arguments["query"].strip()},
                execute=execute,
            )
        )
        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "search", "arguments": {"query": " x "}}]}',
                    '{"type": "answer", "answer": "used tool"}',
                ]
            ),
            registry=registry,
            policy=EffectivePolicy(allowed_tools=["search"]),
        )

        result = await runtime.run_turn(self._workspace())

        self.assertEqual(result.answer, "used tool")
        event_types = [event.event_type for event in repository.events]
        self.assertIn("tool_call_requested", event_types)
        self.assertIn("permission_decision", event_types)
        self.assertIn("tool_result", event_types)

    async def test_runtime_waits_when_tool_requires_permission(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            return ToolResult(
                tool_name="write_resource",
                call_id="call-1",
                ok=True,
                result_kind="result",
                preview="done",
                payload={},
                facts=[],
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="write_resource",
                description="Write",
                input_schema={},
                permission=ToolPermission(scope="write", requires_user_approval=True),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        runtime = HarnessRuntime(
            repository=FakeHarnessRepository(),
            planner=QueuePlanner(
                ['{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "write_resource", "arguments": {}}]}']
            ),
            registry=registry,
            policy=EffectivePolicy(allowed_tools=["write_resource"]),
        )

        result = await runtime.run_turn(self._workspace())

        self.assertEqual(result.metadata["status"], "waiting_permission")

    async def test_runtime_rejects_repeated_tool_call_without_progress(self):
        from ai.harness.errors import PlannerNoProgress
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            return ToolResult(
                tool_name="search",
                call_id="call-1",
                ok=True,
                result_kind="result",
                preview="done",
                payload={},
                facts=[],
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="search",
                description="Search",
                input_schema={},
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        repository = FakeHarnessRepository()
        repository.events = [
            type(
                "Event",
                (),
                {
                    "event_type": "tool_result",
                    "payload": {"tool": "search", "arguments": {"query": "x"}},
                },
            )(),
            type(
                "Event",
                (),
                {
                    "event_type": "tool_result",
                    "payload": {"tool": "search", "arguments": {"query": "x"}},
                },
            )(),
        ]
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "tool_calls", "tool_calls": [{"id": "call-3", "name": "search", "arguments": {"query": "x"}}]}']
            ),
            registry=registry,
            policy=EffectivePolicy(allowed_tools=["search"]),
        )

        with self.assertRaises(PlannerNoProgress):
            await runtime.run_turn(self._workspace())


if __name__ == "__main__":
    unittest.main()
