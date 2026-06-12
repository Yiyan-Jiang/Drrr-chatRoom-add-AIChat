from ai.evals.cases import ReplayCase


def load_minimal_cases() -> list[ReplayCase]:
    return [ReplayCase.from_dict(payload) for payload in _MINIMAL_CASES]


def _input(message: str) -> dict:
    return {
        "request_id": message.replace("_", "-"),
        "session_id": "session-1",
        "user_id": 7,
        "message": message,
    }


def _tool_action(call_id: str, name: str, arguments: dict | None = None) -> dict:
    return {
        "type": "tool_calls",
        "tool_calls": [
            {
                "id": call_id,
                "name": name,
                "arguments": arguments or {},
            }
        ],
    }


def _open_teaching(call_id: str = "open") -> dict:
    return _tool_action(call_id, "open_skill", {"skill_name": "teaching"})


def _answer(text: str = "ok") -> dict:
    return {"type": "answer", "answer": text}


_MINIMAL_CASES = [
    {
        "case_id": "harness_answer",
        "description": "Answer action completes the run.",
        "input": _input("harness_answer"),
        "planner_actions": [_answer()],
        "expected": {"required_actions": ["answer"], "final_status": "completed"},
    },
    {
        "case_id": "harness_ask_user",
        "description": "Ask-user action waits for user input.",
        "input": _input("harness_ask_user"),
        "planner_actions": [{"type": "ask_user", "question": "Which topic?"}],
        "expected": {"required_actions": ["ask_user"], "final_status": "waiting_user"},
    },
    {
        "case_id": "harness_deny",
        "description": "Deny action blocks the run.",
        "input": _input("harness_deny"),
        "planner_actions": [{"type": "deny", "reason": "blocked by replay"}],
        "expected": {"required_actions": ["deny"], "final_status": "blocked"},
    },
    {
        "case_id": "harness_update_checkpoint",
        "description": "Checkpoint update is visible in snapshot history.",
        "input": _input("harness_update_checkpoint"),
        "planner_actions": [
            {"type": "update_checkpoint", "checkpoint": {"phase": "checkpointed"}},
            _answer(),
        ],
        "expected": {
            "required_actions": ["update_checkpoint", "answer"],
            "checkpoint_contains": {"phase": "checkpointed"},
            "checkpoint_path_exists": ["phase"],
            "final_status": "completed",
        },
    },
    {
        "case_id": "harness_complete_artifact",
        "description": "Complete action writes a final-state artifact.",
        "input": _input("harness_complete_artifact"),
        "planner_actions": [
            {"type": "complete", "answer": "completed", "final_state": {"done": True}}
        ],
        "expected": {
            "required_actions": ["complete"],
            "required_artifacts": ["run_final_state"],
            "final_status": "completed",
        },
    },
    {
        "case_id": "harness_tool_allow",
        "description": "Allowed runtime tool writes an artifact.",
        "input": _input("harness_tool_allow"),
        "policy": {"allowed_tools": ["record_note"]},
        "planner_actions": [
            _tool_action("note", "record_note", {"note": "remember this"}),
            _answer(),
        ],
        "expected": {
            "required_tools": ["record_note"],
            "required_permissions": {"record_note": "allow"},
            "required_artifacts": ["runtime_note"],
            "final_status": "completed",
        },
    },
    {
        "case_id": "harness_tool_ask",
        "description": "Ask policy stops before tool execution.",
        "input": _input("harness_tool_ask"),
        "policy": {"allowed_tools": ["record_note"], "ask_tools": ["record_note"]},
        "planner_actions": [_tool_action("note", "record_note", {"note": "needs approval"})],
        "expected": {
            "required_tools": ["record_note"],
            "required_permissions": {"record_note": "ask"},
            "forbidden_artifacts": ["runtime_note"],
            "final_status": "waiting_permission",
        },
    },
    {
        "case_id": "harness_tool_deny",
        "description": "Deny policy stops before tool execution.",
        "input": _input("harness_tool_deny"),
        "policy": {"allowed_tools": ["record_note"], "denied_tools": ["record_note"]},
        "planner_actions": [_tool_action("note", "record_note", {"note": "blocked"})],
        "expected": {
            "required_tools": ["record_note"],
            "required_permissions": {"record_note": "deny"},
            "forbidden_artifacts": ["runtime_note"],
            "final_status": "blocked",
        },
    },
    {
        "case_id": "skill_list",
        "description": "Skill listing tool runs under the default replay policy.",
        "input": _input("skill_list"),
        "planner_actions": [_tool_action("list", "list_skills"), _answer()],
        "expected": {
            "required_tools": ["list_skills"],
            "required_permissions": {"list_skills": "allow"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "skill_open_teaching",
        "description": "Opening teaching skill merges skill state and policy.",
        "input": _input("skill_open_teaching"),
        "planner_actions": [_open_teaching(), _answer()],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["open_skill"],
            "required_permissions": {"open_skill": "allow"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "teaching_path_generation",
        "description": "Teaching path generation writes a path and checkpoint.",
        "input": _input("teaching_path_generation"),
        "planner_actions": [
            _open_teaching(),
            _tool_action(
                "path",
                "generate_learning_path",
                {"goal": "FastAPI basics", "level": "beginner", "time_budget": "7 days"},
            ),
            _answer(),
        ],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["open_skill", "generate_learning_path"],
            "required_artifacts": ["learning_path"],
            "checkpoint_contains": {"skill": "teaching", "next_teaching_action": "explain"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "teaching_practice_followup",
        "description": "Teaching practice asks for a learner answer through checkpoint state.",
        "input": _input("teaching_practice_followup"),
        "planner_actions": [
            _open_teaching(),
            _tool_action(
                "practice",
                "generate_practice",
                {"stage_id": "stage-1", "topic": "routing", "practice_type": "short_answer"},
            ),
            _answer(),
        ],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["generate_practice"],
            "required_artifacts": ["understanding_check"],
            "checkpoint_contains": {"waiting_for": "user_answer", "next_teaching_action": "grade"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "teaching_wrong_answer_remediation",
        "description": "Wrong answer records weak points and routes to remediation.",
        "input": _input("teaching_wrong_answer_remediation"),
        "planner_actions": [
            _open_teaching(),
            _tool_action(
                "grade",
                "grade_answer",
                {
                    "stage_id": "stage-1",
                    "question": "What does routing do?",
                    "expected_answer": "routing maps requests",
                    "user_answer": "no idea",
                },
            ),
            _answer(),
        ],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["grade_answer"],
            "required_artifacts": ["practice_record", "understanding_check"],
            "checkpoint_contains": {"next_teaching_action": "remediate"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "teaching_stage_advance",
        "description": "Stage summary advances the current stage.",
        "input": _input("teaching_stage_advance"),
        "planner_actions": [
            _open_teaching(),
            _tool_action(
                "summary",
                "record_stage_summary",
                {
                    "stage_id": "stage-1",
                    "completed_objectives": ["routing basics"],
                    "mastered_topics": ["routing"],
                    "weak_points": [],
                    "recommended_review": [],
                    "next_stage_id": "stage-2",
                },
            ),
            _answer(),
        ],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["record_stage_summary"],
            "required_artifacts": ["stage_summary"],
            "checkpoint_contains": {"current_stage_id": "stage-2", "next_teaching_action": "explain"},
            "final_status": "completed",
        },
    },
    {
        "case_id": "teaching_review_report",
        "description": "Review report writes the final teaching summary artifact.",
        "input": _input("teaching_review_report"),
        "planner_actions": [
            _open_teaching(),
            _tool_action(
                "review",
                "record_review_report",
                {
                    "goal": "FastAPI basics",
                    "completed_stages": ["stage-1", "stage-2"],
                    "mastery_summary": "Learner can explain routing.",
                    "remaining_gaps": ["dependency injection"],
                    "next_plan": ["review dependencies"],
                },
            ),
            _answer(),
        ],
        "expected": {
            "required_skills": ["teaching"],
            "required_tools": ["record_review_report"],
            "required_artifacts": ["review_report"],
            "checkpoint_contains": {"last_teaching_action": "review"},
            "final_status": "completed",
        },
    },
]
