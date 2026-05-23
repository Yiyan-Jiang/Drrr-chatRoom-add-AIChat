from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from common.normal_database import Login


_ROOM_NAME_LEN = 8


class Room(Login):
    __tablename__ = "chatRoom_room"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(_ROOM_NAME_LEN), unique=True)
    description: str = Column(Text, default="")
    notice: str = Column(Text, default="")
    rules: str = Column(Text, default="")
    tags: list[str] = Column(JSON, default=list)
    min_age: int | None = Column(Integer, nullable=True)
    max_age: int | None = Column(Integer, nullable=True)
    max_members: int = Column(Integer, default=20, nullable=False)
    peak_online_members: int = Column(Integer, default=1, nullable=False)
    owner_id: int | None = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_at: datetime = Column(DateTime, default=datetime.now)
