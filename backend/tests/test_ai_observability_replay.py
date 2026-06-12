import unittest


class FakeRepository:
    def __init__(self):
        self.run = type(
            "Run",
            (),
            {
                "run_id": "run-1",
                "request_id": "request-1",
                "session_id": "session-1",
                "user_id": 7,
                "status": "completed",
                "checkpoint_payload": {"skill": "teaching", "current_stage_id": "stage-1"},
                "skill_state_payload": {
                    "opened_skills": [{"name": "teaching", "version": 1}],
                    "effective_tools": ["generate_learning_path"],
                },
                "created_at": "2026-05-26T12:00:00",
                "completed_at": "2026-05-26T12:01:00",
            },
        )()
        self.audit = type(
            "Audit",
            (),
            {
                "request_id": "request-1",
                "session_id": "session-1",
                "user_id": 7,
                "status": "completed",
                "stage": "completed",
                "error_code": None,
                "error_message": None,
                "debug_payload": None,
            },
        )()
        self.events = [
            type(
                "Event",
                (),
                {
                    "sequence_no": 1,
                    "event_type": "context_compiled",
                    "payload": {"ledger": [{"section": "current_input"}], "token_estimate": 10},
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 2,
                    "event_type": "planner_action",
                    "payload": {
                        "type": "tool_calls",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "name": "generate_learning_path",
                                "arguments": {"goal": "FastAPI"},
                            }
                        ],
                    },
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 3,
                    "event_type": "tool_call_requested",
                    "payload": {
                        "call_id": "call-1",
                        "tool": "generate_learning_path",
                        "arguments": {"goal": "FastAPI"},
                    },
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 4,
                    "event_type": "permission_decision",
                    "payload": {
                        "call_id": "call-1",
                        "tool": "generate_learning_path",
                        "decision": {"kind": "allow", "reason": "allowed"},
                    },
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 5,
                    "event_type": "tool_result",
                    "payload": {
                        "call_id": "call-1",
                        "tool": "generate_learning_path",
                        "arguments": {"goal": "FastAPI"},
                        "result": {"ok": True, "result_kind": "learning_path", "elapsed_ms": 2},
                    },
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 6,
                    "event_type": "artifact_written",
                    "payload": {"artifact_id": "artifact-1", "artifact_type": "learning_path"},
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 7,
                    "event_type": "checkpoint_updated",
                    "payload": {"checkpoint": {"skill": "teaching", "current_stage_id": "stage-1"}},
                },
            )(),
            type(
                "Event",
                (),
                {
                    "sequence_no": 8,
                    "event_type": "skill_opened",
                    "payload": {"name": "teaching", "version": 1, "tools": ["generate_learning_path"]},
                },
            )(),
        ]
        self.artifacts = [
            type(
                "Artifact",
                (),
                {"artifact_type": "learning_path", "payload": {"goal": "FastAPI"}},
            )()
        ]

    async def list_events(self, _run_id):
        return list(self.events)

    async def list_artifacts(self, _run_id):
        return list(self.artifacts)

    async def get_audit_by_request_id(self, _request_id):
        return self.audit


class DebugSnapshotDerivationTest(unittest.IsolatedAsyncioTestCase):
    async def test_debug_snapshot_derives_timelines_and_request_trace(self):
        from ai.evals.debug import build_debug_snapshot

        snapshot = await build_debug_snapshot(FakeRepository(), "run-1")

        self.assertEqual(snapshot["run_id"], "run-1")
        self.assertEqual(snapshot["request"]["request_id"], "request-1")
        self.assertEqual(snapshot["run"]["status"], "completed")
        self.assertEqual(snapshot["context_ledger"][0]["section"], "current_input")
        self.assertEqual(snapshot["planner_actions"][0]["type"], "tool_calls")
        self.assertEqual(snapshot["tool_timeline"][0]["tool"], "generate_learning_path")
        self.assertEqual(snapshot["tool_timeline"][0]["permission"]["kind"], "allow")
        self.assertTrue(snapshot["tool_timeline"][0]["result"]["ok"])
        self.assertEqual(snapshot["permission_timeline"][0]["decision"]["kind"], "allow")
        self.assertEqual(snapshot["artifact_timeline"][0]["artifact_type"], "learning_path")
        self.assertEqual(snapshot["checkpoint_history"][0]["checkpoint"]["skill"], "teaching")
        self.assertEqual(snapshot["skill_state"]["opened_skills"][0]["name"], "teaching")
        self.assertEqual(snapshot["errors"], [])

    async def test_debug_snapshot_collects_error_layers(self):
        from ai.evals.debug import build_debug_snapshot

        repository = FakeRepository()
        repository.audit.status = "failed"
        repository.audit.stage = "runtime_running"
        repository.audit.error_code = "PLANNER_INVALID_ACTION"
        repository.audit.error_message = "bad action"
        repository.run.status = "failed"
        repository.events.append(
            type(
                "Event",
                (),
                {
                    "sequence_no": 9,
                    "event_type": "tool_result",
                    "payload": {
                        "call_id": "call-2",
                        "tool": "grade_answer",
                        "result": {
                            "ok": False,
                            "error_code": "ValueError",
                            "error_message": "bad input",
                        },
                    },
                },
            )()
        )

        snapshot = await build_debug_snapshot(repository, "run-1")

        layers = [error["layer"] for error in snapshot["errors"]]
        self.assertIn("request", layers)
        self.assertIn("tool", layers)


class ReplayCaseTest(unittest.TestCase):
    def test_replay_case_loads_from_dict_and_replay_planner_uses_actions(self):
        from ai.evals.cases import ReplayCase
        from ai.evals.replay import ReplayPlanner

        case = ReplayCase.from_dict(
            {
                "case_id": "teaching_path_generation",
                "description": "path",
                "input": {"request_id": "case-1", "message": "learn FastAPI", "user_id": 7},
                "planner_actions": [{"type": "answer", "answer": "ok"}],
                "expected": {"final_status": "completed"},
            }
        )

        self.assertEqual(case.case_id, "teaching_path_generation")
        self.assertEqual(ReplayPlanner(case.planner_actions).index, 0)


class BenchmarkAssertionExtensionTest(unittest.TestCase):
    def test_benchmark_assertions_check_skills_permissions_checkpoint_and_sequence(self):
        from ai.evals.assertions import assert_snapshot_expectations

        snapshot = {
            "run": {"status": "completed"},
            "planner_actions": [{"type": "tool_calls"}, {"type": "answer"}],
            "tool_timeline": [
                {
                    "tool": "generate_learning_path",
                    "permission": {"kind": "allow"},
                    "result": {"ok": True},
                }
            ],
            "artifact_timeline": [{"artifact_type": "learning_path"}],
            "checkpoint": {"skill": "teaching", "current_stage_id": "stage-1"},
            "skill_state": {"opened_skills": [{"name": "teaching"}]},
            "events": [
                {"event_type": "skill_opened"},
                {"event_type": "tool_call_requested"},
                {"event_type": "tool_result"},
            ],
            "errors": [],
        }

        assert_snapshot_expectations(
            snapshot,
            {
                "required_skills": ["teaching"],
                "required_actions": ["tool_calls"],
                "required_tools": ["generate_learning_path"],
                "required_permissions": {"generate_learning_path": "allow"},
                "required_artifacts": ["learning_path"],
                "checkpoint_contains": {"skill": "teaching"},
                "checkpoint_path_exists": ["current_stage_id"],
                "event_sequence": ["skill_opened", "tool_call_requested", "tool_result"],
                "final_status": "completed",
            },
        )

        with self.assertRaisesRegex(AssertionError, "required skill missing"):
            assert_snapshot_expectations(snapshot, {"required_skills": ["missing"]})


if __name__ == "__main__":
    unittest.main()
