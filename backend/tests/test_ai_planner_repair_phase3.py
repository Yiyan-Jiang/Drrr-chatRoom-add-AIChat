import unittest


class Phase3PlannerRepairTest(unittest.IsolatedAsyncioTestCase):
    def _registry_with_search_tool(self):
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
        return registry

    async def test_plan_with_repair_sends_contract_error_to_next_planner_call(self):
        from ai.harness.actions import AnswerAction
        from ai.harness.context import CompiledContext
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner import plan_with_repair
        from ai.harness.planner_verifier import PlannerVerifier

        class FakePlanner:
            def __init__(self):
                self.outputs = [
                    '{"type": "update_checkpoint", "checkpoint": {"step": "one"}}',
                    '{"type": "answer", "answer": "fixed"}',
                ]
                self.contexts = []

            async def plan(self, context):
                self.contexts.append(context)
                return self.outputs.pop(0)

        planner = FakePlanner()
        action = await plan_with_repair(
            planner,
            CompiledContext(
                messages=[{"role": "user", "content": "hello"}],
                ledger=[],
                token_estimate=0,
            ),
            verifier=PlannerVerifier(),
            registry=self._registry_with_search_tool(),
            policy=EffectivePolicy(allowed_tools=["search"]),
            max_repair_attempts=1,
        )

        self.assertIsInstance(action, AnswerAction)
        self.assertEqual(action.answer, "fixed")
        self.assertEqual(len(planner.contexts), 2)
        repair_message = planner.contexts[1].messages[-1]["content"]
        self.assertIn("action type not allowed", repair_message)
        self.assertIn("Return one corrected JSON object", repair_message)

    async def test_plan_with_repair_stops_after_configured_attempts(self):
        from ai.harness.context import CompiledContext
        from ai.harness.errors import PlannerInvalidAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner import plan_with_repair
        from ai.harness.planner_verifier import PlannerVerifier

        class AlwaysInvalidPlanner:
            def __init__(self):
                self.calls = 0

            async def plan(self, _context):
                self.calls += 1
                return "not json"

        planner = AlwaysInvalidPlanner()

        with self.assertRaises(PlannerInvalidAction) as caught:
            await plan_with_repair(
                planner,
                CompiledContext(messages=[], ledger=[], token_estimate=0),
                verifier=PlannerVerifier(),
                registry=self._registry_with_search_tool(),
                policy=EffectivePolicy(allowed_tools=["search"]),
                max_repair_attempts=2,
            )

        self.assertEqual(planner.calls, 3)
        self.assertIn("planner output invalid after 2 repair attempt", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
