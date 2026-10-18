"""定义帖子、评论、点赞和收藏的持久化结构。"""

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


_POST_TITLE_LEN = 80
_POST_STATUS_LEN = 20


class Post(Login):
    """保存帖子的正文、作者和发布状态。

    Attributes:
        author_id: 作者的用户标识；作者删除后可为空。
        title: 帖子标题。
        content: 帖子正文。
        status: 帖子的发布状态。
        created_at: 帖子创建时间。
        updated_at: 帖子最近更新时间。
    """

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
    status: str = Column(
        String(_POST_STATUS_LEN), default="published", nullable=False, index=True
    )
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class PostComment(Login):
    """保存属于指定帖子的评论。

    Attributes:
        post_id: 评论所属帖子的标识。
        author_id: 评论作者的用户标识；作者删除后可为空。
        content: 评论正文。
        created_at: 评论创建时间。
        updated_at: 评论最近更新时间。
    """

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
    """记录用户对帖子的点赞，同一用户与帖子组合唯一。

    Attributes:
        post_id: 被点赞帖子的标识。
        user_id: 点赞用户的标识。
        created_at: 点赞时间。
    """

    __tablename__ = "chatRoom_post_like"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_like_post_user"),
    )

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
    """记录用户收藏的帖子，同一用户与帖子组合唯一。

    Attributes:
        post_id: 被收藏帖子的标识。
        user_id: 收藏用户的标识。
        created_at: 收藏时间。
    """

    __tablename__ = "chatRoom_post_favorite"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_favorite_post_user"),
    )

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
