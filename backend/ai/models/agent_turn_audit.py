from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ai.database import AIBase


class AgentTurnAudit(AIBase):
    __tablename__ = "agent_turn_audit"

    id: int = Column(Integer, primary_key=True)
    request_id: str = Column(String(80), nullable=False, unique=True, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    session_id: str | None = Column(String(64), nullable=True, index=True)
    status: str = Column(String(20), nullable=False, default="pending", index=True)
    stage: str = Column(String(40), nullable=False, default="reserved")
    response_payload: dict | None = Column(JSON, nullable=True)
    error_code: str | None = Column(String(80), nullable=True)
    error_message: str | None = Column(Text, nullable=True)
    debug_payload: dict | None = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    completed_at: datetime | None = Column(DateTime, nullable=True)
