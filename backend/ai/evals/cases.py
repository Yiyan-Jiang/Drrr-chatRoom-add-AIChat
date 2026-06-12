from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReplayCase:
    case_id: str
    description: str
    input: dict[str, Any]
    planner_actions: list[dict | str]
    expected: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ReplayCase":
        case_id = payload.get("case_id")
        if not case_id:
            raise ValueError("case_id is required")
        return cls(
            case_id=case_id,
            description=payload.get("description", ""),
            input=dict(payload.get("input") or {}),
            planner_actions=list(payload.get("planner_actions") or []),
            expected=dict(payload.get("expected") or {}),
            policy=dict(payload.get("policy") or {}),
        )
