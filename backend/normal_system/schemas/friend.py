from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from normal_system.schemas.user import UserPublic


FriendRequestStatus = Literal["pending", "accepted", "rejected", "canceled"]
FriendRequestDirection = Literal["incoming", "outgoing", "all"]


class FriendRequestCreate(BaseModel):
    recipient_id: int


class FriendRequestInDB(BaseModel):
    id: int
    requester: UserPublic
    recipient: UserPublic
    status: FriendRequestStatus
    created_at: datetime
    updated_at: datetime


class PaginatedFriendRequestsResponse(BaseModel):
    items: list[FriendRequestInDB] = Field(default_factory=list)


class FriendInDB(BaseModel):
    user: UserPublic
    created_at: datetime


class PaginatedFriendsResponse(BaseModel):
    items: list[FriendInDB] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False


class PrivateMessageCreate(BaseModel):
    recipient_id: int
    content: str = Field(..., min_length=1, max_length=3000)
    client_message_id: str | None = Field(default=None, max_length=64)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, value):
        return value.strip() if isinstance(value, str) else value


class PrivateMessageInDB(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    client_message_id: str | None = None
    author: UserPublic
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedPrivateMessagesResponse(BaseModel):
    items: list[PrivateMessageInDB] = Field(default_factory=list)
    has_more: bool = False
    next_before_id: int | None = None
