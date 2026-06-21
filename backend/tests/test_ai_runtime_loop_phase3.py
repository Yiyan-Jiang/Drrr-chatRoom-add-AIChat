import unittest
from unittest.mock import patch


class Phase3RuntimeVerifierIntegrationTest(unittest.IsolatedAsyncioTestCase):
    def _workspace(self):
        from tests.test_ai_harness_phase4 import FakeCommand, FakeWorkspace

        return FakeWorkspace(
            command=FakeCommand(),
            session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
            recent_turns=[],
        )

    async def test_runtime_uses_planner_verifier_before_executing_action(self):
        from ai.harness.errors import PlannerInvalidAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.default_tools import create_default_tool_registry
        from tests.test_ai_harness_phase4 import FakeHarnessRepository, QueuePlanner

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "update_checkpoint", "checkpoint": {"step": "blocked"}}']
            ),
            registry=create_default_tool_registry(),
            policy=EffectivePolicy(allowed_tools=["read_checkpoint"]),
            planner_verifier=PlannerVerifier(),
            max_repair_attempts=0,
        )

        with self.assertRaises(PlannerInvalidAction):
            await runtime.run_turn(self._workspace())

        self.assertEqual(repository.run.status, "failed")
        self.assertEqual(repository.run.error_code, "PLANNER_INVALID_ACTION")
        self.assertNotIn("checkpoint_updated", [event.event_type for event in repository.events])

    async def test_runtime_records_contract_rejected_event_before_repair(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.default_tools import create_default_tool_registry
        from tests.test_ai_harness_phase4 import FakeHarnessRepository, QueuePlanner

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "update_checkpoint", "checkpoint": {"step": "blocked"}}',
                    '{"type": "answer", "answer": "fixed"}',
                ]
            ),
            registry=create_default_tool_registry(),
            policy=EffectivePolicy(allowed_tools=["read_checkpoint"]),
            planner_verifier=PlannerVerifier(),
            max_repair_attempts=1,
        )

        result = await runtime.run_turn(self._workspace())

        self.assertEqual(result.answer, "fixed")
        rejected_events = [
            event for event in repository.events if event.event_type == "contract_rejected"
        ]
        self.assertEqual(len(rejected_events), 1)
        self.assertEqual(rejected_events[0].payload["attempt"], 0)
        self.assertIn("action type not allowed", rejected_events[0].payload["error_message"])

    async def test_runtime_returns_plain_text_fallback_when_markdown_repair_fails(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.default_tools import create_default_tool_registry
        from tests.test_ai_harness_phase4 import FakeHarnessRepository, QueuePlanner

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "answer", "answer": "**Markdown** 可以这样写"}',
                    '{"type": "answer", "answer": "**Markdown** 还是这样写"}',
                ]
            ),
            registry=create_default_tool_registry(),
            policy=EffectivePolicy(allowed_tools=["read_checkpoint"]),
            planner_verifier=PlannerVerifier(),
            max_repair_attempts=1,
        )

        result = await runtime.run_turn(self._workspace())

        self.assertEqual(result.metadata["status"], "completed")
        self.assertNotIn("**", result.answer)
        self.assertIn("普通文字", result.answer)
        rejected_events = [
            event for event in repository.events if event.event_type == "contract_rejected"
        ]
        self.assertEqual(len(rejected_events), 2)

    async def test_runtime_validates_tool_arguments_before_normalize(self):
        from ai.harness.errors import PlannerInvalidAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.harness.runtime import HarnessRuntime
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec
        from tests.test_ai_harness_phase4 import FakeHarnessRepository, QueuePlanner

        async def execute(_context, _arguments):
            raise AssertionError("tool should not execute")

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="search",
                description="Search",
                input_schema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {"query": {"type": "string"}},
                },
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "search", "arguments": {}}]}']
            ),
            registry=registry,
            policy=EffectivePolicy(allowed_tools=["search"]),
            planner_verifier=PlannerVerifier(),
            max_repair_attempts=0,
        )

        with self.assertRaises(PlannerInvalidAction):
            await runtime.run_turn(self._workspace())

        self.assertNotIn("tool_call_requested", [event.event_type for event in repository.events])

class Phase3RuntimeFactoryTest(unittest.TestCase):
    def test_runtime_factory_uses_deterministic_planner_by_default(self):
        from ai.harness.planner import DeterministicAnswerPlanner
        from ai.orchestrator.runtime import build_harness_runtime
        from tests.test_ai_harness_phase4 import FakeHarnessRepository

        with patch.dict("os.environ", {}, clear=True):
            runtime = build_harness_runtime(repository=FakeHarnessRepository())

        self.assertIsInstance(runtime._planner, DeterministicAnswerPlanner)
        self.assertIsNone(runtime._planner_verifier)

    def test_runtime_factory_enables_json_planner_when_configured(self):
        from ai.harness.json_planner import JSONPlannerClient
        from ai.harness.model_config import PlannerModelConfig
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.orchestrator.runtime import build_harness_runtime
        from tests.test_ai_harness_phase4 import FakeHarnessRepository

        class FakeGateway:
            def __init__(self, config):
                self.config = config

        with patch.dict(
            "os.environ",
            {"AGENT_CORE_ENABLE_LLM_PLANNER": "1"},
            clear=True,
        ):
            with patch(
                "ai.orchestrator.runtime.load_planner_model_config",
                return_value=PlannerModelConfig(
                    api_key="key",
                    base_url=None,
                    model="planner-model",
                ),
            ):
                with patch("ai.orchestrator.runtime.ModelGateway", FakeGateway):
                    runtime = build_harness_runtime(repository=FakeHarnessRepository())

        self.assertIsInstance(runtime._planner, JSONPlannerClient)
        self.assertIsInstance(runtime._planner_verifier, PlannerVerifier)


if __name__ == "__main__":
    unittest.main()
