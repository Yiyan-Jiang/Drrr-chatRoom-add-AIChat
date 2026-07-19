from dataclasses import asdict, dataclass, field
from typing import Any

from ai.models.agent_memory import AgentMemory
from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn


@dataclass(frozen=True)
class AITurnCommand:
    request_id: str
    session_id: str | None
    user_id: int
    message: str
    character: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunResult:
    answer: str
    trace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AITurnResult:
    request_id: str
    session_id: str
    answer: str
    status: str
    trace_id: str | None = None
    error_code: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, Any] | None) -> "AITurnResult":
        if payload is None:
            raise ValueError("cached response payload is empty")
        return cls(
            request_id=payload["request_id"],
            session_id=payload["session_id"],
            answer=payload.get("answer", ""),
            status=payload.get("status", "completed"),
            trace_id=payload.get("trace_id"),
            error_code=payload.get("error_code"),
        )


@dataclass(frozen=True)
class TurnWorkspace:
    command: AITurnCommand
    session: AgentSession
    recent_turns: list[AgentTurn]
    long_term_memories: list[AgentMemory] = field(default_factory=list)
