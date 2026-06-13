from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from ai.database import AIBase


class KnowledgeSection(AIBase):
    __tablename__ = "knowledge_sections"
    __table_args__ = (
        UniqueConstraint("document_id", "sequence_no", name="uq_knowledge_sections_document_sequence"),
    )

    id: int = Column(Integer, primary_key=True)
    section_id: str = Column(String(80), nullable=False, unique=True, index=True)
    document_id: str = Column(String(80), nullable=False, index=True)
    title: str = Column(String(300), nullable=False)
    text: str = Column(Text, nullable=False)
    sequence_no: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
