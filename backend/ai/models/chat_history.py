from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ai.database import AIBase

# AI 历史信息表
class AIChatHistory(AIBase):
    __tablename__ = "ai_chat_history"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    character: str = Column(String(20), default="sakura", nullable=False, index=True)
    role: str = Column(String(20), nullable=False)
    content: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)