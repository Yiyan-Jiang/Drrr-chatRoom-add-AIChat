import unittest
from dataclasses import dataclass


@dataclass
class FakeCommand:
    request_id: str = "request-1"
    session_id: str | None = "session-1"
    user_id: int = 7
    message: str = "open a skill"
    character: str | None = None
    metadata: dict | None = None


@dataclass
class FakeWorkspace:
    command: FakeCommand
    session: object
    recent_turns: list


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
                "skill_state_payload": None,
            },
        )()
        self.events = []
        self.artifacts = []

    async def load_or_create_run(self, _workspace):
        return self.run

    async def list_events(self, _run_id):
        return list(self.events)

    async def list_artifacts(self, _run_id):
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

    async def update_skill_state(self, run, skill_state):
        run.skill_state_payload = skill_state
        return run

    async def write_artifact(self, run, artifact_type, payload, request_id=None):
        artifact = type(
            "Artifact",
            (),
            {
                "run_id": run.run_id,
                "artifact_type": artifact_type,
                "payload": payload,
                "request_id": request_id or run.request_id,
            },
        )()
        self.artifacts.append(artifact)
        await self.append_event(
            run.run_id,
            "artifact_written",
            {"artifact_type": artifact_type},
        )
        return artifact

    async def mark_terminal(self, run, status):
        run.status = status
        return run

    async def mark_failed(self, run, error_code, error_message):
        run.status = "failed"
        run.error_code = error_code
        run.error_message = error_message
        return run


class QueuePlanner:
    def __init__(self, outputs):
        self.outputs = list(outputs)

    async def plan(self, _context):
        return self.outputs.pop(0)


def make_workspace():
    return FakeWorkspace(
        command=FakeCommand(),
        session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
        recent_turns=[],
    )


class SkillManifestTest(unittest.TestCase):
    def test_manifest_validates_tools_instruction_and_contracts(self):
        from ai.runtime.default_tools import create_default_tool_registry
        from ai.skills.errors import SkillContractError
        from ai.skills.manifest import SkillManifest

        tool_registry = create_default_tool_registry()

        manifest = SkillManifest(
            name="assistant",
            version=1,
            description="General assistant skill",
            instruction="Use structured runtime tools.",
            tools=["record_note"],
            artifact_contracts={"runtime_note": {"type": "object"}},
            checkpoint_schema={"type": "object"},
            policy={"allow": ["record_note"]},
        )

        manifest.validate(tool_registry)

        with self.assertRaises(SkillContractError):
            SkillManifest(
                name="bad",
                version=1,
                description="Bad",
                instruction="Use unknown tool.",
                tools=["missing_tool"],
                artifact_contracts={},
                checkpoint_schema={},
                policy={},
            ).validate(tool_registry)

        with self.assertRaises(SkillContractError):
            SkillManifest(
                name="bad",
                version=1,
                description="Bad",
                instruction="",
                tools=[],
                artifact_contracts={},
                checkpoint_schema={},
                policy={},
            ).validate(tool_registry)


class SkillRegistryTest(unittest.TestCase):
    def test_static_registry_lists_and_opens_valid_skill(self):
        from ai.runtime.default_tools import create_default_tool_registry
        from ai.skills.errors import SkillNotFound
        from ai.skills.static_registry import create_default_skill_registry

        registry = create_default_skill_registry(create_default_tool_registry())

        summaries = registry.list_skills(user_id=7, workspace_id=None)
        self.assertIn("assistant", [summary["name"] for summary in summaries])

        manifest = registry.open_skill("assistant", user_id=7, workspace_id=None)
        self.assertEqual(manifest.name, "assistant")
        self.assertIn("record_note", manifest.tools)

        with self.assertRaises(SkillNotFound):
            registry.open_skill("missing", user_id=7, workspace_id=None)


class SkillContextTest(unittest.TestCase):
    def test_context_includes_opened_skill_instruction_and_state(self):
        from ai.harness.context import compile_context

        run = type(
            "Run",
            (),
            {
                "run_id": "run-1",
                "checkpoint_payload": None,
                "skill_state_payload": {
                    "opened_skills": [
                        {
                            "name": "assistant",
                            "version": 1,
                            "instruction": "Use structured runtime tools.",
                            "tools": ["record_note"],
                            "artifact_contracts": {"runtime_note": {}},
                            "checkpoint_schema": {},
                        }
                    ],
                    "effective_tools": ["record_note"],
                    "effective_artifacts": ["runtime_note"],
                    "effective_policy": {"allow": ["record_note"]},
                },
            },
        )()

        context = compile_context(
            workspace=make_workspace(),
            run=run,
            events=[],
            artifacts=[],
        )

        sections = [item.section for item in context.ledger]
        joined = "\n".join(message["content"] for message in context.messages)
        self.assertIn("skill_instructions", sections)
        self.assertIn("skill_state", sections)
        self.assertIn("Use structured runtime tools.", joined)


class SkillRuntimeToolTest(unittest.IsolatedAsyncioTestCase):
    async def test_list_skills_tool_returns_available_skills(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "list_skills", "arguments": {}}]}',
                    '{"type": "answer", "answer": "listed"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["list_skills"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.answer, "listed")
        tool_results = [event for event in repository.events if event.event_type == "tool_result"]
        self.assertEqual(tool_results[0].payload["tool"], "list_skills")
        self.assertIn("assistant", tool_results[0].payload["result"]["preview"])

    async def test_open_skill_updates_run_state_and_allows_skill_tool_next_iteration(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "open_skill", "arguments": {"skill_name": "assistant"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-2", "name": "record_note", "arguments": {"note": "hello"}}]}',
                    '{"type": "answer", "answer": "done"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.answer, "done")
        self.assertEqual(repository.run.skill_state_payload["opened_skills"][0]["name"], "assistant")
        self.assertIn("record_note", repository.run.skill_state_payload["effective_tools"])
        self.assertEqual(repository.artifacts[0].artifact_type, "runtime_note")
        self.assertIn("skill_opened", [event.event_type for event in repository.events])

    async def test_permission_deny_prevents_open_skill_side_effect(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "open_skill", "arguments": {"skill_name": "assistant"}}]}']
            ),
            policy=EffectivePolicy(allowed_tools=[]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.metadata["status"], "blocked")
        self.assertIsNone(repository.run.skill_state_payload)

    async def test_base_policy_deny_overrides_skill_allow(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "open_skill", "arguments": {"skill_name": "assistant"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-2", "name": "record_note", "arguments": {"note": "hello"}}]}',
                ]
            ),
            policy=EffectivePolicy(
                allowed_tools=["open_skill"],
                denied_tools=["record_note"],
            ),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.metadata["status"], "blocked")
        self.assertEqual(repository.artifacts, [])

    async def test_artifact_contract_rejects_unlisted_artifact_type(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-1", "name": "open_skill", "arguments": {"skill_name": "assistant"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "call-2", "name": "write_artifact", "arguments": {"artifact_type": "unlisted", "payload": {}}}]}',
                    '{"type": "answer", "answer": "done"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill", "write_artifact"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.answer, "done")
        tool_results = [event for event in repository.events if event.event_type == "tool_result"]
        self.assertFalse(tool_results[-1].payload["result"]["ok"])
        self.assertEqual(repository.artifacts, [])

    async def test_checkpoint_schema_rejects_missing_required_key(self):
        from ai.harness.errors import CheckpointContractError
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        repository.run.skill_state_payload = {
            "opened_skills": [],
            "effective_tools": [],
            "effective_artifacts": [],
            "effective_policy": {},
            "effective_checkpoint_schema": {"required": ["step"]},
        }
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                ['{"type": "update_checkpoint", "checkpoint": {"other": "value"}}']
            ),
            max_iterations=1,
        )

        with self.assertRaises(CheckpointContractError):
            await runtime.run_turn(make_workspace())


if __name__ == "__main__":
    unittest.main()
