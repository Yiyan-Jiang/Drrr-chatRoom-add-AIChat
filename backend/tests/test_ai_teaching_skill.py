import unittest
from dataclasses import dataclass


@dataclass
class FakeCommand:
    request_id: str = "request-1"
    session_id: str | None = "session-1"
    user_id: int = 7
    message: str = "我想学习 Python 异步编程，零基础，每天 30 分钟"
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


def make_workspace(message: str | None = None):
    return FakeWorkspace(
        command=FakeCommand(message=message or FakeCommand.message),
        session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
        recent_turns=[],
    )


class TeachingSkillManifestTest(unittest.TestCase):
    def test_teaching_skill_is_listed_and_opens_with_contracts(self):
        from ai.runtime.default_tools import create_default_tool_registry
        from ai.skills.static_registry import create_default_skill_registry

        tool_registry = create_default_tool_registry()
        skill_registry = create_default_skill_registry(tool_registry)

        summaries = skill_registry.list_skills(user_id=7, workspace_id=None)
        self.assertIn("teaching", [summary["name"] for summary in summaries])

        manifest = skill_registry.open_skill("teaching", user_id=7, workspace_id=None)
        self.assertIn("generate_learning_path", manifest.tools)
        self.assertIn("learning_path", manifest.artifact_contracts)
        self.assertIn("required", manifest.checkpoint_schema)
        manifest.validate(tool_registry)


class TeachingSkillRuntimeTest(unittest.IsolatedAsyncioTestCase):
    async def test_learning_path_tool_writes_artifact_and_checkpoint(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "open", "name": "open_skill", "arguments": {"skill_name": "teaching"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "path", "name": "generate_learning_path", "arguments": {"goal": "Python 异步编程", "level": "beginner", "time_budget": "每天30分钟"}}]}',
                    '{"type": "answer", "answer": "学习路径已生成"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.answer, "学习路径已生成")
        artifacts = {artifact.artifact_type: artifact for artifact in repository.artifacts}
        self.assertIn("learning_path", artifacts)
        self.assertGreaterEqual(len(artifacts["learning_path"].payload["stages"]), 3)
        self.assertEqual(repository.run.checkpoint_payload["skill"], "teaching")
        self.assertEqual(repository.run.checkpoint_payload["goal"], "Python 异步编程")
        self.assertEqual(repository.run.checkpoint_payload["current_stage_id"], "stage-1")

    async def test_explain_and_practice_tools_write_artifacts_and_wait_for_answer(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "open", "name": "open_skill", "arguments": {"skill_name": "teaching"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "explain", "name": "explain_concept", "arguments": {"stage_id": "stage-1", "topic": "事件循环", "level": "beginner", "style": "simple"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "practice", "name": "generate_practice", "arguments": {"stage_id": "stage-1", "topic": "事件循环", "difficulty": "easy", "practice_type": "short_answer"}}]}',
                    '{"type": "ask_user", "question": "请回答这道练习"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.metadata["status"], "waiting_user")
        artifact_types = [artifact.artifact_type for artifact in repository.artifacts]
        self.assertIn("lesson_note", artifact_types)
        self.assertIn("understanding_check", artifact_types)
        self.assertEqual(repository.run.checkpoint_payload["current_topic"], "事件循环")
        self.assertEqual(repository.run.checkpoint_payload["waiting_for"], "user_answer")

    async def test_grade_wrong_answer_records_weak_point_and_remediation(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "open", "name": "open_skill", "arguments": {"skill_name": "teaching"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "grade", "name": "grade_answer", "arguments": {"stage_id": "stage-1", "question": "事件循环是什么？", "expected_answer": "调度异步任务", "user_answer": "不知道"}}]}',
                    '{"type": "answer", "answer": "我们先补救这个知识点"}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill"]),
        )

        await runtime.run_turn(make_workspace("不知道"))

        practice = [a for a in repository.artifacts if a.artifact_type == "practice_record"][0]
        checks = [a for a in repository.artifacts if a.artifact_type == "understanding_check"]
        self.assertEqual(practice.payload["result"], "incorrect")
        self.assertIn("事件循环是什么？", repository.run.checkpoint_payload["weak_points"])
        self.assertEqual(repository.run.checkpoint_payload["next_teaching_action"], "remediate")
        self.assertTrue(checks)

    async def test_stage_summary_advances_checkpoint_and_review_report_completes(self):
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime

        repository = FakeHarnessRepository()
        runtime = HarnessRuntime(
            repository=repository,
            planner=QueuePlanner(
                [
                    '{"type": "tool_calls", "tool_calls": [{"id": "open", "name": "open_skill", "arguments": {"skill_name": "teaching"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "summary", "name": "record_stage_summary", "arguments": {"stage_id": "stage-1", "completed_objectives": ["理解事件循环"], "mastered_topics": ["事件循环"], "weak_points": [], "next_stage_id": "stage-2"}}]}',
                    '{"type": "tool_calls", "tool_calls": [{"id": "review", "name": "record_review_report", "arguments": {"goal": "Python 异步编程", "completed_stages": ["stage-1"], "mastery_summary": "已理解基础", "remaining_gaps": [], "next_plan": ["继续学习 await"]}}]}',
                    '{"type": "complete", "answer": "学习复盘已完成", "final_state": {"skill": "teaching", "review_report": true}}',
                ]
            ),
            policy=EffectivePolicy(allowed_tools=["open_skill"]),
        )

        result = await runtime.run_turn(make_workspace())

        self.assertEqual(result.metadata["status"], "completed")
        artifact_types = [artifact.artifact_type for artifact in repository.artifacts]
        self.assertIn("stage_summary", artifact_types)
        self.assertIn("review_report", artifact_types)
        self.assertIn("run_final_state", artifact_types)
        self.assertEqual(repository.run.checkpoint_payload["current_stage_id"], "stage-2")


if __name__ == "__main__":
    unittest.main()
