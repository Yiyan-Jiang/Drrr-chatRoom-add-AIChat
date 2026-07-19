from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint

from ai.database import AIBase


class AgentMemory(AIBase):
    __tablename__ = "agent_memories"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "character",
            "source_turn_id",
            "memory_type",
            name="uq_agent_memories_source_turn_type",
        ),
    )

    id: int = Column(Integer, primary_key=True)
    memory_id: str = Column(String(80), nullable=False, unique=True, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    character: str | None = Column(String(20), nullable=True, index=True)
    session_id: str = Column(String(64), nullable=False, index=True)
    source_turn_id: int | None = Column(Integer, nullable=True, index=True)
    source_sequence_no: int | None = Column(Integer, nullable=True)
    memory_type: str = Column(String(40), nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    importance: int = Column(Integer, nullable=False, default=3)
    confidence: float = Column(Float, nullable=False, default=0.8)
    status: str = Column(String(20), nullable=False, default="active", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    last_used_at: datetime | None = Column(DateTime, nullable=True)
