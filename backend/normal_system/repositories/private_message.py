"""读写两人私聊消息并按消息 ID 分页，不提交事务。"""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import PrivateMessage, User
from normal_system.schemas.friend import (
    PaginatedPrivateMessagesResponse,
    PrivateMessageInDB,
)


def _serialize_private_message(
    message: PrivateMessage, author: User
) -> PrivateMessageInDB:
    """组合私聊消息与发送者公开资料。"""
    return PrivateMessageInDB(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        content=message.content,
        client_message_id=message.client_message_id,
        author=author,
        created_at=message.created_at,
    )


async def get_private_message_by_client_message_id(
    db: AsyncSession,
    client_message_id: str,
) -> PrivateMessage | None:
    """按客户端消息标识读取已有私聊消息，用于识别重放。"""
    res = await db.execute(
        select(PrivateMessage).where(
            PrivateMessage.client_message_id == client_message_id
        )
    )
    return res.scalar_one_or_none()


def add_private_message(db: AsyncSession, **fields) -> PrivateMessage:
    """把私聊消息加入会话，不提交事务。"""
    message = PrivateMessage(**fields)
    db.add(message)
    return message


async def list_private_messages(
    db: AsyncSession,
    user_id: int,
    friend_id: int,
    limit: int = 20,
    before_id: int | None = None,
) -> PaginatedPrivateMessagesResponse:
    """按消息 ID 倒序读取两名用户之间的私聊历史。

    Args:
        db: 查询使用的数据库会话。
        user_id: 查询发起方的用户 ID。
        friend_id: 会话另一方的用户 ID；本查询不校验好友关系。
        limit: 请求条数，当前实现将其限制在 1 到 50 条。
        before_id: 排他消息 ID 游标；为空时读取最新一页。

    Returns:
        包含发送者公开资料的历史页及后续消息游标。
    """
    safe_limit = max(1, min(limit, 50))
    filters = [
        or_(
            and_(
                PrivateMessage.sender_id == user_id,
                PrivateMessage.recipient_id == friend_id,
            ),
            and_(
                PrivateMessage.sender_id == friend_id,
                PrivateMessage.recipient_id == user_id,
            ),
        )
    ]
    if before_id is not None:
        filters.append(PrivateMessage.id < before_id)

    res = await db.execute(
        select(PrivateMessage, User)
        .join(User, PrivateMessage.sender_id == User.id)
        .where(*filters)
        .order_by(PrivateMessage.id.desc())
        .limit(safe_limit + 1)
    )
    rows = res.all()
    has_more = len(rows) > safe_limit
    page_rows = rows[:safe_limit]
    items = [
        _serialize_private_message(message, author) for message, author in page_rows
    ]
    return PaginatedPrivateMessagesResponse(
        items=items,
        has_more=has_more,
        next_before_id=items[-1].id if has_more and items else None,
    )
