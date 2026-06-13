from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ai.database import AIBase


class KnowledgeDocument(AIBase):
    __tablename__ = "knowledge_documents"

    id: int = Column(Integer, primary_key=True)
    document_id: str = Column(String(80), nullable=False, unique=True, index=True)
    title: str = Column(String(300), nullable=False)
    source: str = Column(String(120), nullable=False)
    owner_user_id: int = Column(Integer, nullable=False, index=True)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    raw_content: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
