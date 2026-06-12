from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, UniqueConstraint

from ai.database import AIBase


class HarnessEvent(AIBase):
    __tablename__ = "harness_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence_no", name="uq_harness_events_run_sequence"),
    )

    id: int = Column(Integer, primary_key=True)
    run_id: str = Column(String(80), nullable=False, index=True)
    sequence_no: int = Column(Integer, nullable=False)
    event_type: str = Column(String(80), nullable=False, index=True)
    payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)