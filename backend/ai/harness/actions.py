import json
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError

from ai.harness.errors import ActionParseError


class ToolCall(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    arguments: dict = Field(default_factory=dict)


class AnswerAction(BaseModel):
    type: Literal["answer"]
    answer: str = Field(..., min_length=1)


class AskUserAction(BaseModel):
    type: Literal["ask_user"]
    question: str = Field(..., min_length=1)


class ToolCallsAction(BaseModel):
    type: Literal["tool_calls"]
    tool_calls: list[ToolCall] = Field(default_factory=list)


class UpdateCheckpointAction(BaseModel):
    type: Literal["update_checkpoint"]
    checkpoint: dict = Field(..., min_length=1)


class CompleteAction(BaseModel):
    type: Literal["complete"]
    answer: str = Field(..., min_length=1)
    final_state: dict = Field(default_factory=dict)


class DenyAction(BaseModel):
    type: Literal["deny"]
    reason: str = Field(..., min_length=1)


PlannerAction = Union[
    AnswerAction,
    AskUserAction,
    ToolCallsAction,
    UpdateCheckpointAction,
    CompleteAction,
    DenyAction,
]


def _validate(model_class, data: dict) -> PlannerAction:
    try:
        action = model_class(**data)
    except ValidationError as exc:
        raise ActionParseError(str(exc)) from exc

    if isinstance(action, ToolCallsAction) and not action.tool_calls:
        raise ActionParseError("tool_calls requires at least one call")

    return action


def extract_json_object(raw: str) -> dict:
    start = raw.find("{")
    if start < 0:
        raise ActionParseError("planner output does not contain a JSON object")

    decoder = json.JSONDecoder()
    try:
        data, _ = decoder.raw_decode(raw[start:])
    except json.JSONDecodeError as exc:
        raise ActionParseError(str(exc)) from exc

    if not isinstance(data, dict):
        raise ActionParseError("planner output JSON must be an object")
    return data


def parse_action(raw: str) -> PlannerAction:
    data = extract_json_object(raw)
    action_type = data.get("type")

    if action_type is None and isinstance(data.get("answer"), str):
        return _validate(AnswerAction, {"type": "answer", "answer": data["answer"]})

    if action_type == "answer":
        return _validate(AnswerAction, data)
    if action_type == "ask_user":
        return _validate(AskUserAction, data)
    if action_type == "tool_calls":
        return _validate(ToolCallsAction, data)
    if action_type == "update_checkpoint":
        return _validate(UpdateCheckpointAction, data)
    if action_type == "complete":
        return _validate(CompleteAction, data)
    if action_type == "deny":
        return _validate(DenyAction, data)

    raise ActionParseError(f"unknown action type: {action_type}")
