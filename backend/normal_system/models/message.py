"""定义聊天室消息的持久化结构。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from common.normal_database import Login


_MESSAGE_TYPE_LEN = 20
_CLIENT_MESSAGE_ID_LEN = 64


class Message(Login):
    """保存房间内的用户消息或系统消息。

    Attributes:
        user_id: 发送者的用户标识；用户删除后可为空。
        content: 消息正文。
        room_id: 消息所属房间的标识。
        message_type: 区分用户消息与系统消息的类型。
        client_message_id: 客户端提供的可选消息标识，在表内唯一。
        created_at: 消息创建时间。
    """

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
    message_type: str = Column(
        String(_MESSAGE_TYPE_LEN), default="user", nullable=False
    )
    client_message_id: str | None = Column(
        String(_CLIENT_MESSAGE_ID_LEN), unique=True, nullable=True
    )
    created_at: datetime = Column(DateTime, default=datetime.now)
