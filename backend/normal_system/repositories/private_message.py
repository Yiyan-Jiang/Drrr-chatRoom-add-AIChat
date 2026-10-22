"""读写两人私聊消息并按消息 ID 分页，不提交事务。"""

from datetime import datetime

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from normal_system.models import PrivateMessage, User
from normal_system.schemas.friend import (
    PaginatedPrivateMessagesResponse,
    PrivateMessageInDB,
    PrivateConversation,
    PrivateConversationsResponse,
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


async def list_private_conversations(
    db: AsyncSession, user_id: int, page: int, page_size: int
) -> PrivateConversationsResponse:
    """按当前用户参与的消息聚合会话，分页读取最新消息和未读数量。"""
    partner = case(
        (PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id),
        else_=PrivateMessage.sender_id,
    )
    conversations = (
        select(
            partner.label("partner_id"),
            func.max(PrivateMessage.id).label("latest_id"),
            func.sum(
                case(
                    (
                        and_(
                            PrivateMessage.recipient_id == user_id,
                            PrivateMessage.read_at.is_(None),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("unread_count"),
        )
        .where(
            or_(
                PrivateMessage.sender_id == user_id,
                PrivateMessage.recipient_id == user_id,
            )
        )
        .group_by(partner)
        .subquery()
    )
    author = aliased(User)
    rows = (
        await db.execute(
            select(User, PrivateMessage, author, conversations.c.unread_count)
            .select_from(conversations)
            .join(User, User.id == conversations.c.partner_id)
            .join(PrivateMessage, PrivateMessage.id == conversations.c.latest_id)
            .join(author, author.id == PrivateMessage.sender_id)
            .order_by(conversations.c.latest_id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size + 1)
        )
    ).all()
    return PrivateConversationsResponse(
        items=[
            PrivateConversation(
                user=user,
                latest_message=_serialize_private_message(message, sender),
                unread_count=int(unread),
            )
            for user, message, sender, unread in rows[:page_size]
        ],
        has_more=len(rows) > page_size,
    )


async def mark_private_messages_read(
    db: AsyncSession, user_id: int, friend_id: int, through_id: int
) -> bool:
    """只标记当前用户从会话对象收到的消息；边界不属于该收件会话时返回 False。"""
    boundary = await db.scalar(
        select(PrivateMessage.id).where(
            PrivateMessage.id == through_id,
            PrivateMessage.sender_id == friend_id,
            PrivateMessage.recipient_id == user_id,
        )
    )
    if boundary is None:
        return False
    await db.execute(
        update(PrivateMessage)
        .where(
            PrivateMessage.sender_id == friend_id,
            PrivateMessage.recipient_id == user_id,
            PrivateMessage.id <= through_id,
            PrivateMessage.read_at.is_(None),
        )
        .values(read_at=datetime.now())
    )
    return True
