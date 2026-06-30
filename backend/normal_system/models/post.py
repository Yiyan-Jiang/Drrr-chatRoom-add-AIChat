from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from common.normal_database import Login


_POST_TITLE_LEN = 80
_POST_STATUS_LEN = 20


class Post(Login):
    __tablename__ = "chatRoom_post"

    id: int = Column(Integer, primary_key=True)
    author_id: int | None = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: str = Column(String(_POST_TITLE_LEN), nullable=False)
    content: str = Column(Text, nullable=False)
    status: str = Column(String(_POST_STATUS_LEN), default="published", nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class PostComment(Login):
    __tablename__ = "chatRoom_post_comment"

    id: int = Column(Integer, primary_key=True)
    post_id: int = Column(
        Integer,
        ForeignKey("chatRoom_post.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: int | None = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class PostLike(Login):
    __tablename__ = "chatRoom_post_like"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_post_like_post_user"),)

    id: int = Column(Integer, primary_key=True)
    post_id: int = Column(
        Integer,
        ForeignKey("chatRoom_post.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class PostFavorite(Login):
    __tablename__ = "chatRoom_post_favorite"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_post_favorite_post_user"),)

    id: int = Column(Integer, primary_key=True)
    post_id: int = Column(
        Integer,
        ForeignKey("chatRoom_post.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: int = Column(
        Integer,
        ForeignKey("chatRoom_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
