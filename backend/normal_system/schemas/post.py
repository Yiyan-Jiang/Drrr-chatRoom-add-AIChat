"""定义帖子、评论及相关列表分页的数据结构。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from normal_system.schemas.user import UserPublic


class PostCreate(BaseModel):
    """接收待发布帖子的标题和正文。"""

    title: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=20000)

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value):
        """清除标题或正文字符串两端的空白。

        Args:
            value: 字段校验前收到的文本值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value


class PostCommentCreate(BaseModel):
    """接收待发布评论的正文。"""

    content: str = Field(..., min_length=1, max_length=3000)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, value):
        """清除评论字符串两端的空白。

        Args:
            value: 字段校验前收到的评论正文。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value


class PostCommentInDB(BaseModel):
    """返回评论正文、所属帖子、作者和时间信息。"""

    id: int
    post_id: int
    content: str
    author: Optional[UserPublic] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostCommentListItem(PostCommentInDB):
    """在评论记录上补充所属帖子的标题和正文预览。"""

    post_title: str
    post_content_preview: str


class PostListItem(BaseModel):
    """返回帖子预览、互动统计及当前用户的点赞状态。"""

    id: int
    title: str
    content_preview: str
    author: Optional[UserPublic] = None
    comments_count: int = 0
    likes_count: int = 0
    favorites_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    updated_at: datetime


class PostDetail(PostListItem):
    """在帖子列表资料上补充完整正文和当前用户的收藏状态。"""

    content: str
    favorited_by_me: bool = False


class PaginatedPostsResponse(BaseModel):
    """返回帖子列表及后续记录的分页游标。"""

    items: list[PostListItem]
    has_more: bool = False
    next_cursor: Optional[int] = None


class PaginatedCommentsResponse(BaseModel):
    """返回帖子评论列表及后续记录的分页游标。"""

    items: list[PostCommentInDB]
    has_more: bool = False
    next_cursor: Optional[int] = None


class PaginatedMyCommentsResponse(BaseModel):
    """返回当前用户的评论列表及后续记录的分页游标。"""

    items: list[PostCommentListItem]
    has_more: bool = False
    next_cursor: Optional[int] = None
