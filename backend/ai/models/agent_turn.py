from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, UniqueConstraint

from ai.database import AIBase


class AgentTurn(AIBase):
    __tablename__ = "agent_turns"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence_no", name="uq_agent_turns_session_sequence"),
    )

    id: int = Column(Integer, primary_key=True)
    session_id: str = Column(String(64), nullable=False, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    sequence_no: int = Column(Integer, nullable=False)
    role: str = Column(String(20), nullable=False)
    content: str = Column(Text, nullable=False)
    request_id: str | None = Column(String(80), nullable=True, index=True)
    character: str | None = Column(String(20), nullable=True)
    extra_payload: dict | None = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
