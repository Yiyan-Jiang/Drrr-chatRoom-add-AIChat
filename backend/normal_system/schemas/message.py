from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from normal_system.schemas.user import UserPublic


class MessageBase(BaseModel):
    content: str
    room_id: Optional[int] = None
    client_message_id: Optional[str] = Field(default=None, max_length=64)

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(MessageBase):
    pass


class MessageInDB(MessageBase):
    id: int
    user_id: Optional[int]
    message_type: Literal["user", "system"] = "user"
    author: Optional[UserPublic] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedMessagesResponse(BaseModel):
    items: List[MessageInDB] = Field(default_factory=list)
    has_more: bool
    next_before_id: Optional[int] = None
