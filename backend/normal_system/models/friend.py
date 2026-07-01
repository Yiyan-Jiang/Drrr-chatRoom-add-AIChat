from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from common.normal_database import Login


_REQUEST_STATUS_LEN = 20
_CLIENT_MESSAGE_ID_LEN = 64


class FriendRequest(Login):
    __tablename__ = "chatRoom_friend_request"
    __table_args__ = (
        UniqueConstraint("requester_id", "recipient_id", "status", name="uq_friend_request_direction_status"),
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
    status: str = Column(String(_REQUEST_STATUS_LEN), default="pending", nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class Friendship(Login):
    __tablename__ = "chatRoom_friendship"
    __table_args__ = (UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_pair"),)

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
    client_message_id: str | None = Column(String(_CLIENT_MESSAGE_ID_LEN), unique=True, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False, index=True)
