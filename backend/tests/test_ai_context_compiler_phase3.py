import unittest
from types import SimpleNamespace


class Phase3ContextCompilerTest(unittest.TestCase):
    def _workspace(self):
        from tests.test_ai_harness_phase4 import FakeCommand, FakeWorkspace

        return FakeWorkspace(
            command=FakeCommand(message="use the tool"),
            session=SimpleNamespace(session_id="session-1", user_id=7),
            recent_turns=[],
        )

    def _workspace_for_character(self, character: str):
        from tests.test_ai_harness_phase4 import FakeCommand, FakeWorkspace

        return FakeWorkspace(
            command=FakeCommand(message="hello", character=character),
            session=SimpleNamespace(session_id="session-1", user_id=7),
            recent_turns=[],
        )

    def _workspace_with_recent_turns(self):
        from tests.test_ai_harness_phase4 import FakeCommand, FakeWorkspace

        return FakeWorkspace(
            command=FakeCommand(message="what did I ask before?"),
            session=SimpleNamespace(session_id="session-1", user_id=7),
            recent_turns=[
                SimpleNamespace(
                    sequence_no=1,
                    role="user",
                    content="I want to learn asyncio",
                    character="sakura",
                ),
                SimpleNamespace(
                    sequence_no=2,
                    role="assistant",
                    content="We can start with event loops.",
                    character="sakura",
                ),
            ],
        )

    def _registry(self):
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
                description="Search indexed content.",
                input_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                },
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        registry.register(
            ToolSpec(
                name="secret_write",
                description="Should not be visible.",
                input_schema={"type": "object", "properties": {}},
                permission=ToolPermission(scope="write"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        return registry

    def test_compile_context_includes_policy_tools_artifacts_and_observations(self):
        from ai.harness.context import compile_context
        from ai.harness.permissions import EffectivePolicy

        context = compile_context(
            workspace=self._workspace(),
            run=SimpleNamespace(run_id="run-1", checkpoint_payload={"step": "tool"}),
            events=[
                SimpleNamespace(
                    event_type="tool_result",
                    payload={
                        "call_id": "call-1",
                        "tool": "search",
                        "result": {
                            "ok": True,
                            "result_kind": "result",
                            "preview": "found item",
                        },
                    },
                )
            ],
            artifacts=[
                SimpleNamespace(
                    artifact_id="artifact-1",
                    artifact_type="planner_note",
                    payload={"summary": "short artifact", "body": "long body"},
                )
            ],
            registry=self._registry(),
            policy=EffectivePolicy(
                allowed_tools=["search", "secret_write"],
                denied_tools=["secret_write"],
            ),
        )

        sections = [item.section for item in context.ledger]
        self.assertIn("run_policy", sections)
        self.assertIn("tool_schemas", sections)
        self.assertIn("artifact_summaries", sections)
        self.assertIn("observations", sections)

        content = "\n".join(message["content"] for message in context.messages)
        self.assertIn("search", content)
        self.assertNotIn("secret_write", content)
        self.assertIn("short artifact", content)
        self.assertIn("found item", content)
        self.assertIn("answer", content)
        self.assertIn("tool_calls", content)

    def test_compile_context_injects_character_system_prompt(self):
        from ai.harness.context import compile_context

        context = compile_context(
            workspace=self._workspace_for_character("sakura"),
            run=SimpleNamespace(run_id="run-1", checkpoint_payload={}),
            events=[],
            artifacts=[],
        )

        sections = [item.section for item in context.ledger]
        self.assertIn("character_prompt", sections)

        content = "\n".join(message["content"] for message in context.messages)
        self.assertIn("小樱", content)
        self.assertIn("傲娇", content)

    def test_compile_context_includes_recent_turn_content(self):
        from ai.harness.context import compile_context

        context = compile_context(
            workspace=self._workspace_with_recent_turns(),
            run=SimpleNamespace(run_id="run-1", checkpoint_payload={}),
            events=[],
            artifacts=[],
        )

        sections = [item.section for item in context.ledger]
        self.assertIn("recent_turns", sections)

        content = "\n".join(message["content"] for message in context.messages)
        self.assertIn("I want to learn asyncio", content)
        self.assertIn("We can start with event loops.", content)
        self.assertIn('"role": "user"', content)
        self.assertIn('"sequence_no": 1', content)


if __name__ == "__main__":
    unittest.main()
