from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, UniqueConstraint

from ai.database import AIBase


class KnowledgeChunk(AIBase):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        UniqueConstraint("section_id", "sequence_no", name="uq_knowledge_chunks_section_sequence"),
    )

    id: int = Column(Integer, primary_key=True)
    chunk_id: str = Column(String(80), nullable=False, unique=True, index=True)
    document_id: str = Column(String(80), nullable=False, index=True)
    section_id: str = Column(String(80), nullable=False, index=True)
    text: str = Column(Text, nullable=False)
    sequence_no: int = Column(Integer, nullable=False)
    lexical_terms: list[str] | None = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
