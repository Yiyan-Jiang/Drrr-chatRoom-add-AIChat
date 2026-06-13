from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ai.database import AIBase


class KnowledgeJob(AIBase):
    __tablename__ = "knowledge_jobs"

    id: int = Column(Integer, primary_key=True)
    job_id: str = Column(String(80), nullable=False, unique=True, index=True)
    job_type: str = Column(String(80), nullable=False, index=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    status: str = Column(String(30), nullable=False, default="pending", index=True)
    payload: dict | None = Column(JSON, nullable=True)
    error_code: str | None = Column(String(80), nullable=True)
    error_message: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    completed_at: datetime | None = Column(DateTime, nullable=True)
