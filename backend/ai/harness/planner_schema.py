LLM_PLANNER_ALLOWED_ACTIONS = ["answer", "ask_user", "tool_calls"]


def get_llm_planner_action_schema() -> dict:
    return {
        "allowed_actions": list(LLM_PLANNER_ALLOWED_ACTIONS),
        "actions": {
            "answer": {
                "type": "object",
                "required": ["type", "answer"],
                "properties": {
                    "type": {"const": "answer"},
                    "answer": {"type": "string", "minLength": 1},
                },
            },
            "ask_user": {
                "type": "object",
                "required": ["type", "question"],
                "properties": {
                    "type": {"const": "ask_user"},
                    "question": {"type": "string", "minLength": 1},
                },
            },
            "tool_calls": {
                "type": "object",
                "required": ["type", "tool_calls"],
                "properties": {
                    "type": {"const": "tool_calls"},
                    "tool_calls": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["id", "name", "arguments"],
                            "properties": {
                                "id": {"type": "string", "minLength": 1},
                                "name": {"type": "string", "minLength": 1},
                                "arguments": {"type": "object"},
                            },
                        },
                    },
                },
            },
        },
    }
