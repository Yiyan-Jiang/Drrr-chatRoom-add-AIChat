from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from ai.database import AIBase


class AgentArtifact(AIBase):
    __tablename__ = "agent_artifacts"

    id: int = Column(Integer, primary_key=True)
    artifact_id: str = Column(String(80), nullable=False, unique=True, index=True)
    session_id: str | None = Column(String(64), nullable=True, index=True)
    run_id: str | None = Column(String(80), nullable=True, index=True)
    request_id: str | None = Column(String(80), nullable=True, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    artifact_type: str = Column(String(80), nullable=False, index=True)
    payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)