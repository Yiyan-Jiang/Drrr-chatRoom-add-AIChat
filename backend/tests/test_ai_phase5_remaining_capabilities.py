import unittest

from tests.test_ai_harness_phase4 import FakeCommand, FakeHarnessRepository, FakeWorkspace


def make_workspace(session_id="session-1", user_id=7):
    return FakeWorkspace(
        command=FakeCommand(session_id=session_id, user_id=user_id),
        session=type("Session", (), {"session_id": session_id, "user_id": user_id})(),
        recent_turns=[],
    )


class ResourceCapabilityTest(unittest.IsolatedAsyncioTestCase):
    async def test_resource_visibility_and_tools(self):
        from ai.resources.models import AgentResource
        from ai.resources.tools import register_resource_tools
        from ai.resources.visibility import can_see_resource
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.tools import ToolExecutionContext

        workspace = make_workspace()
        visible = AgentResource(
            resource_id="res-1",
            owner_user_id=7,
            scope="session",
            session_id="session-1",
            title="部署手册",
            content="部署步骤是安装依赖。",
        )
        hidden = AgentResource(
            resource_id="res-2",
            owner_user_id=8,
            scope="user",
            session_id=None,
            title="别人的资源",
            content="hidden",
        )

        self.assertTrue(can_see_resource(workspace, visible))
        self.assertFalse(can_see_resource(workspace, hidden))

        registry = ToolRegistry()
        register_resource_tools(registry, [visible, hidden])
        ctx = ToolExecutionContext(
            run_id="run-1",
            session_id="session-1",
            user_id=7,
            call_id="call-1",
        )

        listed = await registry.get("list_resources").execute(ctx, {"workspace": workspace})
        opened = await registry.get("open_resource").execute(
            ctx,
            {"workspace": workspace, "resource_id": "res-1"},
        )

        self.assertEqual(len(listed.payload["resources"]), 1)
        self.assertEqual(opened.payload["resource_id"], "res-1")


class ListingCapabilityTest(unittest.IsolatedAsyncioTestCase):
    async def test_listing_search_tool_writes_listing_state_artifact(self):
        from ai.listing.models import ListingItem
        from ai.listing.tools import register_listing_tools
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.tools import ToolExecutionContext

        artifacts = []

        async def artifact_writer(ctx, artifact_type, payload):
            artifact = type(
                "Artifact",
                (),
                {
                    "artifact_id": "listing-artifact-1",
                    "artifact_type": artifact_type,
                    "payload": payload,
                },
            )()
            artifacts.append(artifact)
            return artifact

        registry = ToolRegistry()
        register_listing_tools(
            registry,
            [
                ListingItem(item_id="item-1", title="部署服务", attributes={"tag": "deploy"}),
                ListingItem(item_id="item-2", title="测试服务", attributes={"tag": "test"}),
            ],
            artifact_writer=artifact_writer,
        )
        ctx = ToolExecutionContext(
            run_id="run-1",
            session_id="session-1",
            user_id=7,
            call_id="call-1",
        )

        result = await registry.get("listing_search").execute(ctx, {"query": "部署"})

        self.assertEqual(result.result_kind, "listing_result")
        self.assertEqual(result.payload["artifact_id"], "listing-artifact-1")
        self.assertEqual(artifacts[0].artifact_type, "listing_state")


class MemoryCapabilityTest(unittest.TestCase):
    def test_memory_worker_refreshes_summary_and_extracts_memory_items(self):
        from ai.memory.models import AgentMemoryItem, ConversationSummary
        from ai.memory.worker import extract_memory_for_turn, refresh_summary

        turns = [
            type("Turn", (), {"sequence_no": 1, "role": "user", "content": "我喜欢部署自动化"})(),
            type("Turn", (), {"sequence_no": 2, "role": "assistant", "content": "我记住了"})(),
        ]

        summary = refresh_summary(
            previous=ConversationSummary(session_id="session-1", text="", source_last_sequence_no=0),
            turns=turns,
        )
        items = [item for turn in turns for item in extract_memory_for_turn("user-7", "session-1", turn)]

        self.assertEqual(summary.source_last_sequence_no, 2)
        self.assertIn("部署自动化", summary.text)
        self.assertTrue(all(isinstance(item, AgentMemoryItem) for item in items))


class DebugSnapshotTest(unittest.IsolatedAsyncioTestCase):
    async def test_debug_snapshot_includes_run_events_artifacts_and_checkpoint(self):
        from ai.evals.debug import build_debug_snapshot

        repository = FakeHarnessRepository()
        repository.run.checkpoint_payload = {"step": "done"}
        repository.events.append(
            type("Event", (), {"event_type": "answer", "payload": {"answer": "ok"}})()
        )
        repository.artifacts = [type("Artifact", (), {"artifact_type": "response_refs", "payload": {}})()]

        async def list_artifacts(_run_id):
            return list(repository.artifacts)

        repository.list_artifacts = list_artifacts

        snapshot = await build_debug_snapshot(repository, "run-1")

        self.assertEqual(snapshot["run_id"], "run-1")
        self.assertEqual(snapshot["checkpoint"], {"step": "done"})
        self.assertEqual(snapshot["events"][0]["event_type"], "answer")
        self.assertEqual(snapshot["artifacts"][0]["artifact_type"], "response_refs")


if __name__ == "__main__":
    unittest.main()
