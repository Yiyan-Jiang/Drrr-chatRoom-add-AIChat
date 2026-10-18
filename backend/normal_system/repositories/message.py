"""查询和序列化群聊消息，写入操作由调用方提交。"""

from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from normal_system.models import Message, User
from normal_system.schemas import MessageInDB, UserPublic


def serialize_message(message: Message, author: User | None = None) -> MessageInDB:
    """把群聊消息及可选作者资料转换为公开响应。"""
    return MessageInDB(
        id=message.id,
        content=message.content,
        room_id=message.room_id,
        client_message_id=message.client_message_id,
        user_id=message.user_id,
        message_type=message.message_type or "user",
        author=UserPublic.model_validate(author) if author else None,
        created_at=message.created_at,
    )


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
    """按消息 ID 读取群聊消息，不存在时返回 None。"""
    res = await db.execute(select(Message).filter(Message.id == message_id))
    return res.scalar_one_or_none()


async def get_message_by_room(db: AsyncSession, room_id: int) -> List[Message]:
    """读取房间最近五十条消息，按创建时间倒序返回。"""
    res = await db.execute(
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    messages: List[Message] = res.scalars().all()
    return messages


async def get_messages_with_authors_by_room(
    db: AsyncSession,
    room_id: int,
    limit: int = 50,
) -> List[MessageInDB]:
    """联查房间消息与作者资料，按创建时间倒序返回。"""
    res = await db.execute(
        select(Message, User)
        .outerjoin(User, Message.user_id == User.id)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = res.all()
    return [serialize_message(message, author) for message, author in rows]


async def get_messages_page_by_room(
    db: AsyncSession,
    room_id: int,
    limit: int = 10,
    before_id: int | None = None,
) -> tuple[list[MessageInDB], bool, int | None]:
    """按消息 ID 倒序读取群聊历史页。

    Args:
        db: 查询使用的数据库会话。
        room_id: 所属房间 ID。
        limit: 请求条数，当前实现将其限制在 1 到 30 条。
        before_id: 只读取小于此 ID 的消息；为空时读取最新一页。

    Returns:
        消息列表、是否还有更旧消息，以及存在下一页时的消息 ID 游标。
    """
    safe_limit = max(1, min(limit, 30))
    filters = [Message.room_id == room_id]
    if before_id is not None:
        filters.append(Message.id < before_id)

    res = await db.execute(
        select(Message, User)
        .outerjoin(User, Message.user_id == User.id)
        .where(*filters)
        .order_by(Message.id.desc())
        .limit(safe_limit + 1)
    )
    rows = res.all()
    has_more = len(rows) > safe_limit
    page_rows = rows[:safe_limit]
    items = [serialize_message(message, author) for message, author in page_rows]
    next_before_id = items[-1].id if has_more and items else None
    return items, has_more, next_before_id


async def get_message_by_client_message_id(
    db: AsyncSession, client_message_id: str
) -> Optional[Message]:
    """按客户端消息标识读取已有群聊消息，用于识别重放。"""
    res = await db.execute(
        select(Message).where(Message.client_message_id == client_message_id)
    )
    return res.scalar_one_or_none()


def add_message(db: AsyncSession, **fields) -> Message:
    """把群聊消息加入会话，不提交事务。"""
    message = Message(**fields)
    db.add(message)
    return message


async def remove_message(db: AsyncSession, message: Message) -> None:
    """在会话中标记删除消息，不提交事务。"""
    await db.delete(message)


async def delete_messages_by_room(db: AsyncSession, room_id: int) -> int:
    """删除房间内全部消息并返回受影响行数，不提交事务。"""
    res = await db.execute(delete(Message).where(Message.room_id == room_id))
    return res.rowcount or 0
