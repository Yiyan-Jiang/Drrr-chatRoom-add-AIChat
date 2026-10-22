"""定义好友申请、好友列表和私聊消息的数据结构。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from normal_system.schemas.user import UserPublic


FriendRequestStatus = Literal["pending", "accepted", "rejected", "canceled"]
FriendRequestDirection = Literal["incoming", "outgoing", "all"]


class FriendRequestCreate(BaseModel):
    """接收好友申请目标用户的标识。"""

    recipient_id: int


class FriendRequestInDB(BaseModel):
    """返回好友申请双方的公开资料、状态及处理时间。"""

    id: int
    requester: UserPublic
    recipient: UserPublic
    status: FriendRequestStatus
    created_at: datetime
    updated_at: datetime


class PaginatedFriendRequestsResponse(BaseModel):
    """返回好友申请记录集合。"""

    items: list[FriendRequestInDB] = Field(default_factory=list)


class FriendInDB(BaseModel):
    """返回好友公开资料及关系建立时间。"""

    user: UserPublic
    created_at: datetime


class PaginatedFriendsResponse(BaseModel):
    """返回好友列表、总数和页码信息。"""

    items: list[FriendInDB] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False


class PrivateMessageCreate(BaseModel):
    """接收私聊目标、正文和可选的客户端消息标识。"""

    recipient_id: int
    content: str = Field(..., min_length=1, max_length=3000)
    client_message_id: str | None = Field(default=None, max_length=64)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, value):
        """清除字符串正文两端的空白。

        Args:
            value: 字段校验前收到的正文值。

        Returns:
            去除两端空白的字符串；非字符串输入原样返回。
        """
        return value.strip() if isinstance(value, str) else value


class PrivateMessageInDB(BaseModel):
    """返回私聊记录及发送者的公开资料。"""

    id: int
    sender_id: int
    recipient_id: int
    content: str
    client_message_id: str | None = None
    author: UserPublic
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedPrivateMessagesResponse(BaseModel):
    """返回私聊记录及向更早消息翻页的游标。

    Attributes:
        items: 本次返回的私聊记录。
        has_more: 是否还有更早的记录。
        next_before_id: 查询下一批更早记录时使用的消息标识。
    """

    items: list[PrivateMessageInDB] = Field(default_factory=list)
    has_more: bool = False
    next_before_id: int | None = None


class PrivateConversation(BaseModel):
    """返回会话对象、最新消息及当前用户收到的未读数量。"""

    user: UserPublic
    latest_message: PrivateMessageInDB
    unread_count: int


class PrivateConversationsResponse(BaseModel):
    """返回按最新消息排序的会话分页。"""

    items: list[PrivateConversation]
    has_more: bool


class PrivateReadRequest(BaseModel):
    """使用已显示的接收消息编号限制本次已读更新范围。"""

    through_id: int = Field(gt=0, strict=True)
