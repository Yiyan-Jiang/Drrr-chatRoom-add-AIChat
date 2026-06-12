from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from ai.database import AIBase


class OutboxEvent(AIBase):
    __tablename__ = "outbox_events"

    id: int = Column(Integer, primary_key=True)
    event_id: str = Column(String(80), nullable=False, unique=True, index=True)
    event_type: str = Column(String(80), nullable=False, index=True)
    aggregate_type: str = Column(String(40), nullable=False)
    aggregate_id: str = Column(String(80), nullable=False, index=True)
    payload: dict = Column(JSON, nullable=False)
    status: str = Column(String(20), nullable=False, default="pending", index=True)
    attempts: int = Column(Integer, nullable=False, default=0)
    next_attempt_at: datetime = Column(DateTime, default=datetime.now, nullable=False, index=True)
    locked_at: datetime | None = Column(DateTime, nullable=True)
    locked_by: str | None = Column(String(80), nullable=True)
    last_error: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    published_at: datetime | None = Column(DateTime, nullable=True)