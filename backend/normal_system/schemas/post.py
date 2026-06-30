from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from normal_system.schemas.user import UserPublic


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=20000)

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class PostCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, value):
        return value.strip() if isinstance(value, str) else value


class PostCommentInDB(BaseModel):
    id: int
    post_id: int
    content: str
    author: Optional[UserPublic] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostCommentListItem(PostCommentInDB):
    post_title: str
    post_content_preview: str


class PostListItem(BaseModel):
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
    content: str
    favorited_by_me: bool = False


class PaginatedPostsResponse(BaseModel):
    items: list[PostListItem]
    has_more: bool = False
    next_cursor: Optional[int] = None


class PaginatedCommentsResponse(BaseModel):
    items: list[PostCommentInDB]
    has_more: bool = False
    next_cursor: Optional[int] = None


class PaginatedMyCommentsResponse(BaseModel):
    items: list[PostCommentListItem]
    has_more: bool = False
    next_cursor: Optional[int] = None
