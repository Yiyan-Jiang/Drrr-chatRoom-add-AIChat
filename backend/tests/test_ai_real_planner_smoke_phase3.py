import os
import unittest


class Phase3RealPlannerSmokeTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if os.environ.get("AGENT_CORE_ENABLE_REAL_PLANNER_SMOKE") != "1":
            self.skipTest("set AGENT_CORE_ENABLE_REAL_PLANNER_SMOKE=1 to run")

        missing = [
            name
            for name in (
                "DEEPSEEK_API_KEY",
            )
            if not os.environ.get(name)
        ]
        if missing:
            self.fail(f"missing real planner smoke env var(s): {', '.join(missing)}")

    async def test_real_planner_outputs_contract_json(self):
        from ai.harness.actions import AnswerAction, AskUserAction, ToolCallsAction
        from ai.harness.context import CompiledContext
        from ai.harness.json_planner import JSONPlannerClient
        from ai.harness.model_config import load_planner_model_config
        from ai.harness.model_gateway import ModelGateway
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.planner import plan_with_repair
        from ai.harness.planner_verifier import PlannerVerifier
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, arguments):
            return ToolResult(
                tool_name="echo_tool",
                call_id="smoke-call",
                ok=True,
                result_kind="echo",
                preview=arguments["text"],
                payload={"text": arguments["text"]},
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="echo_tool",
                description="Echo fixed text for smoke testing.",
                input_schema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {"text": {"type": "string"}},
                },
                permission=ToolPermission(scope="runtime_state"),
                normalize=lambda arguments: arguments,
                execute=execute,
                when_to_use="Use when asked to prove tool call JSON works.",
            )
        )
        policy = EffectivePolicy(allowed_tools=["echo_tool"])
        context = CompiledContext(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return exactly one JSON object. Allowed action types are "
                        "answer, ask_user, tool_calls. If using a tool, call only "
                        "echo_tool with arguments {\"text\": \"smoke\"}."
                    ),
                },
                {
                    "role": "user",
                    "content": "Produce a valid planner JSON action for the smoke test.",
                },
            ],
            ledger=[],
            token_estimate=0,
        )

        action = await plan_with_repair(
            JSONPlannerClient(ModelGateway(load_planner_model_config())),
            context,
            verifier=PlannerVerifier(),
            registry=registry,
            policy=policy,
            max_repair_attempts=2,
        )

        self.assertIsInstance(action, (AnswerAction, AskUserAction, ToolCallsAction))


if __name__ == "__main__":
    unittest.main()
