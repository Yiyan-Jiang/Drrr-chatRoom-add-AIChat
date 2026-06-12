from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ai.database import AIBase


class HarnessRun(AIBase):
    __tablename__ = "harness_runs"

    id: int = Column(Integer, primary_key=True)
    run_id: str = Column(String(80), nullable=False, unique=True, index=True)
    session_id: str | None = Column(String(64), nullable=True, index=True)
    request_id: str | None = Column(String(80), nullable=True, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    status: str = Column(String(30), nullable=False, default="created", index=True)
    checkpoint_payload: dict | None = Column(JSON, nullable=True)
    skill_state_payload: dict | None = Column(JSON, nullable=True)
    error_code: str | None = Column(String(80), nullable=True)
    error_message: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    completed_at: datetime | None = Column(DateTime, nullable=True)
