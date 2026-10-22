"""定义好友申请、好友关系和私聊消息的持久化结构。"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from common.normal_database import Login


_REQUEST_STATUS_LEN = 20
_CLIENT_MESSAGE_ID_LEN = 64


class FriendRequest(Login):
    """记录有方向的好友申请及其处理状态。

    Attributes:
        requester_id: 申请发起者的用户标识。
        recipient_id: 申请接收者的用户标识。
        status: 申请状态；同一方向与状态的组合具有唯一约束。
        created_at: 申请创建时间。
        updated_at: 申请状态最近更新时间。
    """

    __tablename__ = "chatRoom_friend_request"
    __table_args__ = (
        UniqueConstraint(
            "requester_id",
            "recipient_id",
            "status",
            name="uq_friend_request_direction_status",
        ),
    )

    id: int = Column(Integer, primary_key=True)
    requester_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: str = Column(
        String(_REQUEST_STATUS_LEN), default="pending", nullable=False, index=True
    )
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class Friendship(Login):
    """记录由一对用户标识确定的好友关系。

    Attributes:
        user_low_id: 好友双方中较小的用户标识。
        user_high_id: 好友双方中较大的用户标识。
        created_at: 好友关系建立时间。
    """

    __tablename__ = "chatRoom_friendship"
    __table_args__ = (
        UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_pair"),
    )

    id: int = Column(Integer, primary_key=True)
    user_low_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_high_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class PrivateMessage(Login):
    """保存发给指定用户的私聊消息。

    Attributes:
        sender_id: 发送者的用户标识。
        recipient_id: 接收者的用户标识。
        content: 私聊正文。
        read_at: 接收方阅读时间，空值表示未读。
        client_message_id: 客户端提供的可选消息标识，在表内唯一。
        created_at: 消息创建时间。
    """

    __tablename__ = "chatRoom_private_message"

    id: int = Column(Integer, primary_key=True)
    sender_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: str = Column(Text, nullable=False)
    read_at: datetime | None = Column(DateTime, nullable=True)
    client_message_id: str | None = Column(
        String(_CLIENT_MESSAGE_ID_LEN), unique=True, nullable=True
    )
    created_at: datetime = Column(
        DateTime, default=datetime.now, nullable=False, index=True
    )
