import unittest


class AgentBenchmarkTest(unittest.IsolatedAsyncioTestCase):
    async def test_minimal_replay_suite_runs_core_case_types(self):
        from ai.evals.minimal_cases import load_minimal_cases
        from ai.evals.runner import run_replay_case

        cases = load_minimal_cases()
        case_ids = {case.case_id for case in cases}

        self.assertIn("harness_answer", case_ids)
        self.assertIn("harness_tool_ask", case_ids)
        self.assertIn("harness_tool_deny", case_ids)
        self.assertIn("skill_open_teaching", case_ids)
        self.assertIn("teaching_wrong_answer_remediation", case_ids)
        self.assertIn("teaching_review_report", case_ids)

        results = [await run_replay_case(case) for case in cases]

        failures = {result.case_id: result.error for result in results if result.status != "passed"}
        self.assertEqual(failures, {})

    async def test_minimal_teaching_benchmark_case_runs_with_fixed_actions(self):
        from ai.evals.assertions import assert_snapshot_expectations
        from ai.evals.cases import ReplayCase
        from ai.evals.debug import build_debug_snapshot
        from ai.evals.runner import run_replay_case

        case = ReplayCase.from_dict(
            {
                "case_id": "teaching_path_generation",
                "description": "User goal produces teaching path artifact.",
                "input": {
                    "request_id": "case-1",
                    "session_id": "session-1",
                    "user_id": 7,
                    "message": "我想 7 天学会 FastAPI 基础",
                },
                "planner_actions": [
                    {
                        "type": "tool_calls",
                        "tool_calls": [
                            {
                                "id": "open",
                                "name": "open_skill",
                                "arguments": {"skill_name": "teaching"},
                            }
                        ],
                    },
                    {
                        "type": "tool_calls",
                        "tool_calls": [
                            {
                                "id": "path",
                                "name": "generate_learning_path",
                                "arguments": {
                                    "goal": "FastAPI 基础",
                                    "level": "beginner",
                                    "time_budget": "7天",
                                },
                            }
                        ],
                    },
                    {"type": "answer", "answer": "学习路径已生成"},
                ],
                "expected": {
                    "required_skills": ["teaching"],
                    "required_tools": ["open_skill", "generate_learning_path"],
                    "required_artifacts": ["learning_path"],
                    "checkpoint_contains": {"skill": "teaching"},
                    "final_status": "completed",
                },
            }
        )

        result = await run_replay_case(case)
        snapshot = await build_debug_snapshot(result.repository, "run-1")

        self.assertEqual(result.case_id, "teaching_path_generation")
        self.assertEqual(result.status, "passed")
        assert_snapshot_expectations(snapshot, case.expected)


if __name__ == "__main__":
    unittest.main()
