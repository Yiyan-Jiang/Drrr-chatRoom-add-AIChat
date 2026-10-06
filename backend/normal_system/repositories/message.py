from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from normal_system.models import Message, User
from normal_system.schemas import MessageInDB, UserPublic


def serialize_message(message: Message, author: User | None = None) -> MessageInDB:
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
    res = await db.execute(select(Message).filter(Message.id == message_id))
    return res.scalar_one_or_none()


async def get_message_by_room(db: AsyncSession, room_id: int) -> List[Message]:
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
    res = await db.execute(
        select(Message).where(Message.client_message_id == client_message_id)
    )
    return res.scalar_one_or_none()


def add_message(db: AsyncSession, **fields) -> Message:
    message = Message(**fields)
    db.add(message)
    return message


async def remove_message(db: AsyncSession, message: Message) -> None:
    await db.delete(message)


async def delete_messages_by_room(db: AsyncSession, room_id: int) -> int:
    res = await db.execute(delete(Message).where(Message.room_id == room_id))
    return res.rowcount or 0
