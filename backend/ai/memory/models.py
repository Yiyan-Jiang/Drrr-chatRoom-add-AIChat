from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationSummary:
    session_id: str
    text: str
    source_last_sequence_no: int


@dataclass(frozen=True)
class AgentMemoryItem:
    user_id: int
    session_id: str
    memory_type: str
    content: str
    source_sequence_no: int
    importance: int = 3
    confidence: float = 0.8
