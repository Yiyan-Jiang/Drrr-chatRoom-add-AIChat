from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from ai.database import AIBase


class AgentSession(AIBase):
    __tablename__ = "agent_sessions"

    id: int = Column(Integer, primary_key=True)
    session_id: str = Column(String(64), nullable=False, unique=True, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    title: str | None = Column(String(200), nullable=True)
    status: str = Column(String(20), nullable=False, default="active", index=True)
    last_sequence_no: int = Column(Integer, nullable=False, default=0)
    summary_version: int = Column(Integer, nullable=False, default=0)
    extra_payload: dict | None = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
