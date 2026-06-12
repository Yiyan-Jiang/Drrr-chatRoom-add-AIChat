import unittest
from types import SimpleNamespace


class FakeArtifactCheckpointRepository:
    def __init__(self):
        self.artifacts = []
        self.updated_checkpoints = []

    async def list_artifacts(self, run_id):
        return [artifact for artifact in self.artifacts if artifact.run_id == run_id]

    async def update_checkpoint(self, run, checkpoint):
        run.checkpoint_payload = checkpoint
        self.updated_checkpoints.append(checkpoint)
        return run


class Phase3ArtifactCheckpointToolTest(unittest.IsolatedAsyncioTestCase):
    def _context(self, repository, run=None):
        from ai.runtime.tools import ToolExecutionContext

        run = run or SimpleNamespace(
            run_id="run-1",
            checkpoint_payload={"step": "start"},
            skill_state_payload=None,
        )
        return ToolExecutionContext(
            run_id=run.run_id,
            session_id="session-1",
            user_id=7,
            call_id="call-1",
            checkpoint_payload=run.checkpoint_payload,
            run=run,
            repository=repository,
        )

    async def test_read_artifact_returns_matching_artifact_summary(self):
        from ai.runtime.default_tools import create_default_tool_registry

        repository = FakeArtifactCheckpointRepository()
        repository.artifacts.append(
            SimpleNamespace(
                run_id="run-1",
                artifact_id="artifact-1",
                artifact_type="planner_note",
                payload={"summary": "short note", "body": "long body"},
            )
        )
        tool = create_default_tool_registry().get("read_artifact")

        result = await tool.execute(
            self._context(repository),
            tool.normalize({"artifact_id": "artifact-1"}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.result_kind, "artifact")
        self.assertEqual(result.payload["artifact"]["artifact_id"], "artifact-1")
        self.assertEqual(result.payload["artifact"]["artifact_type"], "planner_note")
        self.assertEqual(result.preview, "short note")

    async def test_read_artifact_returns_structured_miss(self):
        from ai.runtime.default_tools import create_default_tool_registry

        tool = create_default_tool_registry().get("read_artifact")

        result = await tool.execute(
            self._context(FakeArtifactCheckpointRepository()),
            tool.normalize({"artifact_id": "missing"}),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "ARTIFACT_NOT_FOUND")

    async def test_update_checkpoint_merges_patch_with_current_checkpoint(self):
        from ai.runtime.default_tools import create_default_tool_registry

        repository = FakeArtifactCheckpointRepository()
        run = SimpleNamespace(
            run_id="run-1",
            checkpoint_payload={"step": "start", "kept": True},
            skill_state_payload=None,
        )
        tool = create_default_tool_registry().get("update_checkpoint")

        result = await tool.execute(
            self._context(repository, run),
            tool.normalize({"patch": {"step": "after_tool"}}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(run.checkpoint_payload, {"step": "after_tool", "kept": True})
        self.assertEqual(
            result.payload["checkpoint"],
            {"step": "after_tool", "kept": True},
        )


if __name__ == "__main__":
    unittest.main()
