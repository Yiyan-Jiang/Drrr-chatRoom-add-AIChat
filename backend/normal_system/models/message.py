from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from common.normal_database import Login


_MESSAGE_TYPE_LEN = 20
_CLIENT_MESSAGE_ID_LEN = 64


class Message(Login):
    __tablename__ = "chatRoom_message"
    id: int = Column(Integer, primary_key=True)
    user_id: int | None = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="SET NULL"),
        nullable=True,
    )
    content: str = Column(Text)
    room_id: int = Column(
        Integer,
        ForeignKey("chatRoom_room.id", ondelete="CASCADE"),
        index=True,
    )
    message_type: str = Column(String(_MESSAGE_TYPE_LEN), default="user", nullable=False)
    client_message_id: str | None = Column(String(_CLIENT_MESSAGE_ID_LEN), unique=True, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now)
