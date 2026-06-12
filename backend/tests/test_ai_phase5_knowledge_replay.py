import unittest

from tests.test_ai_harness_phase4 import FakeCommand, FakeHarnessRepository, FakeWorkspace


def make_workspace(message="部署步骤是什么？"):
    return FakeWorkspace(
        command=FakeCommand(message=message),
        session=type("Session", (), {"session_id": "session-1", "user_id": 7})(),
        recent_turns=[],
    )


class KnowledgeRetrievalTest(unittest.TestCase):
    def test_lexical_search_returns_matching_candidates(self):
        from ai.knowledge.models import KnowledgeDocument, KnowledgeSection
        from ai.knowledge.repositories import InMemoryKnowledgeStore
        from ai.knowledge.retrieval import search_knowledge

        store = InMemoryKnowledgeStore(
            documents=[
                KnowledgeDocument(
                    document_id="doc-1",
                    title="部署手册",
                    source="test",
                    owner_user_id=7,
                )
            ],
            sections=[
                KnowledgeSection(
                    section_id="sec-1",
                    document_id="doc-1",
                    title="部署步骤",
                    text="部署步骤是安装依赖、运行迁移、启动服务。",
                )
            ],
        )

        candidates = search_knowledge(store, "部署步骤", top_k=5)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].document_id, "doc-1")
        self.assertEqual(candidates[0].section_id, "sec-1")


class KnowledgeToolsTest(unittest.IsolatedAsyncioTestCase):
    def _store(self):
        from ai.knowledge.models import KnowledgeDocument, KnowledgeSection
        from ai.knowledge.repositories import InMemoryKnowledgeStore

        return InMemoryKnowledgeStore(
            documents=[
                KnowledgeDocument(
                    document_id="doc-1",
                    title="部署手册",
                    source="test",
                    owner_user_id=7,
                )
            ],
            sections=[
                KnowledgeSection(
                    section_id="sec-1",
                    document_id="doc-1",
                    title="部署步骤",
                    text="部署步骤是安装依赖、运行迁移、启动服务。",
                )
            ],
        )

    async def test_knowledge_tools_search_open_and_extract_response_refs(self):
        from ai.knowledge.tools import register_knowledge_tools
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.tools import ToolExecutionContext

        artifacts = []

        async def artifact_writer(ctx, artifact_type, payload):
            artifact = type(
                "Artifact",
                (),
                {
                    "artifact_id": "artifact-1",
                    "artifact_type": artifact_type,
                    "payload": payload,
                },
            )()
            artifacts.append(artifact)
            return artifact

        registry = ToolRegistry()
        register_knowledge_tools(registry, self._store(), artifact_writer=artifact_writer)
        ctx = ToolExecutionContext(
            run_id="run-1",
            session_id="session-1",
            user_id=7,
            call_id="call-1",
        )

        search = await registry.get("search_knowledge").execute(
            ctx,
            {"query": "部署步骤", "top_k": 5},
        )
        opened = await registry.get("open_knowledge_document").execute(
            ctx,
            {"document_id": "doc-1"},
        )
        evidence = await registry.get("extract_knowledge_evidence").execute(
            ctx,
            {
                "document_id": "doc-1",
                "section_ids": ["sec-1"],
                "question": "部署步骤是什么？",
            },
        )

        self.assertEqual(search.result_kind, "knowledge_candidates")
        self.assertEqual(opened.result_kind, "knowledge_document")
        self.assertEqual(evidence.result_kind, "evidence_pack")
        self.assertEqual(artifacts[0].artifact_type, "response_refs")
        self.assertEqual(evidence.payload["artifact_id"], "artifact-1")


class ReplayBenchmarkTest(unittest.IsolatedAsyncioTestCase):
    async def test_replay_planner_returns_actions_as_json(self):
        from ai.evals.replay import ReplayPlanner
        from ai.harness.actions import ToolCallsAction, parse_action
        from ai.harness.context import CompiledContext

        planner = ReplayPlanner(
            [
                {
                    "type": "tool_calls",
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "name": "search_knowledge",
                            "arguments": {"query": "部署步骤"},
                        }
                    ],
                }
            ]
        )

        raw = await planner.plan(CompiledContext(messages=[], ledger=[], token_estimate=0))
        action = parse_action(raw)

        self.assertIsInstance(action, ToolCallsAction)

    def test_benchmark_assertions_check_tools_artifacts_and_status(self):
        from ai.evals.assertions import assert_benchmark_expectations

        events = [
            type("Event", (), {"event_type": "tool_call_requested", "payload": {"tool": "search_knowledge"}})(),
            type("Event", (), {"event_type": "tool_call_requested", "payload": {"tool": "open_knowledge_document"}})(),
            type("Event", (), {"event_type": "tool_call_requested", "payload": {"tool": "extract_knowledge_evidence"}})(),
        ]
        artifacts = [type("Artifact", (), {"artifact_type": "response_refs"})()]
        result = type("Result", (), {"metadata": {"status": "completed"}, "answer": "安装依赖"})()

        assert_benchmark_expectations(
            events=events,
            artifacts=artifacts,
            result=result,
            expected={
                "required_tools": [
                    "search_knowledge",
                    "open_knowledge_document",
                    "extract_knowledge_evidence",
                ],
                "required_artifacts": ["response_refs"],
                "final_status": "completed",
                "answer_contains": ["安装依赖"],
            },
        )

    async def test_harness_replay_runs_knowledge_tools_and_writes_response_refs(self):
        from ai.evals.assertions import assert_benchmark_expectations
        from ai.evals.replay import ReplayPlanner
        from ai.harness.permissions import EffectivePolicy
        from ai.harness.runtime import HarnessRuntime
        from ai.knowledge.models import KnowledgeDocument, KnowledgeSection
        from ai.knowledge.repositories import InMemoryKnowledgeStore
        from ai.knowledge.tools import register_knowledge_tools
        from ai.runtime.registry import ToolRegistry

        store = InMemoryKnowledgeStore(
            documents=[
                KnowledgeDocument(
                    document_id="doc-1",
                    title="部署手册",
                    source="test",
                    owner_user_id=7,
                )
            ],
            sections=[
                KnowledgeSection(
                    section_id="sec-1",
                    document_id="doc-1",
                    title="部署步骤",
                    text="部署步骤是安装依赖、运行迁移、启动服务。",
                )
            ],
        )
        repository = FakeHarnessRepository()
        repository.artifacts = []

        async def artifact_writer(ctx, artifact_type, payload):
            artifact = type(
                "Artifact",
                (),
                {
                    "artifact_id": "artifact-1",
                    "artifact_type": artifact_type,
                    "payload": payload,
                },
            )()
            repository.artifacts.append(artifact)
            repository.events.append(
                type(
                    "Event",
                    (),
                    {
                        "event_type": "artifact_written",
                        "payload": {"artifact_type": artifact_type},
                    },
                )()
            )
            return artifact

        async def list_artifacts(_run_id):
            return list(repository.artifacts)

        repository.list_artifacts = list_artifacts
        registry = ToolRegistry()
        register_knowledge_tools(registry, store, artifact_writer=artifact_writer)
        planner = ReplayPlanner(
            [
                {
                    "type": "tool_calls",
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "name": "search_knowledge",
                            "arguments": {"query": "部署步骤"},
                        }
                    ],
                },
                {
                    "type": "tool_calls",
                    "tool_calls": [
                        {
                            "id": "call-2",
                            "name": "open_knowledge_document",
                            "arguments": {"document_id": "doc-1"},
                        }
                    ],
                },
                {
                    "type": "tool_calls",
                    "tool_calls": [
                        {
                            "id": "call-3",
                            "name": "extract_knowledge_evidence",
                            "arguments": {
                                "document_id": "doc-1",
                                "section_ids": ["sec-1"],
                                "question": "部署步骤是什么？",
                            },
                        }
                    ],
                },
                {
                    "type": "answer",
                    "answer": "部署步骤是安装依赖、运行迁移、启动服务。",
                },
            ]
        )
        runtime = HarnessRuntime(
            repository=repository,
            planner=planner,
            registry=registry,
            policy=EffectivePolicy(
                allowed_tools=[
                    "search_knowledge",
                    "open_knowledge_document",
                    "extract_knowledge_evidence",
                ]
            ),
        )

        result = await runtime.run_turn(make_workspace())

        assert_benchmark_expectations(
            events=repository.events,
            artifacts=repository.artifacts,
            result=result,
            expected={
                "required_tools": [
                    "search_knowledge",
                    "open_knowledge_document",
                    "extract_knowledge_evidence",
                ],
                "required_artifacts": ["response_refs"],
                "final_status": "completed",
                "answer_contains": ["安装依赖", "运行迁移", "启动服务"],
            },
        )


if __name__ == "__main__":
    unittest.main()
