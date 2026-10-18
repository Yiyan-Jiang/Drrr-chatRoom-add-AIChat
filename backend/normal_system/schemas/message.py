"""定义房间消息的创建、展示与游标分页结构。"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from normal_system.schemas.user import UserPublic


class MessageBase(BaseModel):
    """描述消息正文、可选房间标识和客户端消息标识。"""

    content: str
    room_id: Optional[int] = None
    client_message_id: Optional[str] = Field(default=None, max_length=64)

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(MessageBase):
    """接收创建房间消息所需的数据。"""

    pass


class MessageInDB(MessageBase):
    """返回消息记录、消息类型及可选的作者资料。"""

    id: int
    user_id: Optional[int]
    message_type: Literal["user", "system"] = "user"
    author: Optional[UserPublic] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedMessagesResponse(BaseModel):
    """返回房间消息及向更早消息翻页的游标。

    Attributes:
        items: 本次返回的消息记录。
        has_more: 是否还有更早的记录。
        next_before_id: 查询下一批更早记录时使用的消息标识。
    """

    items: List[MessageInDB] = Field(default_factory=list)
    has_more: bool
    next_before_id: Optional[int] = None
