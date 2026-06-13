import unittest


class Phase3PlannerActionSchemaTest(unittest.TestCase):
    def test_llm_planner_schema_exposes_only_phase3_action_subset(self):
        from ai.harness.planner_schema import get_llm_planner_action_schema

        schema = get_llm_planner_action_schema()

        self.assertEqual(
            schema["allowed_actions"],
            ["answer", "ask_user", "tool_calls"],
        )
        self.assertNotIn("complete", schema["allowed_actions"])
        self.assertNotIn("deny", schema["allowed_actions"])
        self.assertNotIn("update_checkpoint", schema["allowed_actions"])


class Phase3PlannerVerifierTest(unittest.TestCase):
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

    def test_verifier_rejects_runtime_actions_not_allowed_for_llm_planner(self):
        from ai.harness.actions import UpdateCheckpointAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerContractError, PlannerVerifier

        verifier = PlannerVerifier()

        with self.assertRaises(PlannerContractError) as caught:
            verifier.verify(
                UpdateCheckpointAction(type="update_checkpoint", checkpoint={"step": "one"}),
                registry=self._registry_with_search_tool(),
                policy=EffectivePolicy(allowed_tools=["search"]),
            )

        self.assertIn("action type not allowed", str(caught.exception))

    def test_verifier_rejects_unregistered_tool_before_runtime_execution(self):
        from ai.harness.actions import ToolCall, ToolCallsAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerContractError, PlannerVerifier

        verifier = PlannerVerifier()

        with self.assertRaises(PlannerContractError) as caught:
            verifier.verify(
                ToolCallsAction(
                    type="tool_calls",
                    tool_calls=[ToolCall(id="call-1", name="missing", arguments={})],
                ),
                registry=self._registry_with_search_tool(),
                policy=EffectivePolicy(allowed_tools=["missing"]),
            )

        self.assertIn("tool not registered", str(caught.exception))
        self.assertIn("tool_calls[0].name", str(caught.exception))

    def test_verifier_rejects_tool_not_allowed_by_policy(self):
        from ai.harness.actions import ToolCall, ToolCallsAction
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner_verifier import PlannerContractError, PlannerVerifier

        verifier = PlannerVerifier()

        with self.assertRaises(PlannerContractError) as caught:
            verifier.verify(
                ToolCallsAction(
                    type="tool_calls",
                    tool_calls=[ToolCall(id="call-1", name="search", arguments={})],
                ),
                registry=self._registry_with_search_tool(),
                policy=EffectivePolicy(allowed_tools=[]),
            )

        self.assertIn("tool not allowed by policy", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
