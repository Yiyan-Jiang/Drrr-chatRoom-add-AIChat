from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import Message
from normal_system.repositories.message import add_message, get_message_by_client_message_id, get_message_by_id, remove_message
from normal_system.repositories.room import get_room_by_id
from normal_system.schemas import MessageCreate


async def create_message(
    db: AsyncSession,
    message: MessageCreate,
    user_id: int | None,
    message_type: str = "user",
) -> Message:
    room = await get_room_by_id(db, message.room_id)
    if not room:
        raise ValueError(f"Room {message.room_id} does not exist")

    if message.client_message_id:
        existing = await get_message_by_client_message_id(db, message.client_message_id)
        if existing:
            if existing.user_id != user_id or existing.room_id != message.room_id:
                raise ValueError("client_message_id belongs to another conversation")
            return existing

    db_message = add_message(
        db,
        content=message.content,
        room_id=message.room_id,
        user_id=user_id,
        message_type=message_type,
        client_message_id=message.client_message_id,
        created_at=datetime.now(),
    )
    try:
        await db.commit()
        await db.refresh(db_message)
        return db_message
    except IntegrityError:
        await db.rollback()
        if message.client_message_id:
            existing = await get_message_by_client_message_id(db, message.client_message_id)
            if existing:
                if existing.user_id != user_id or existing.room_id != message.room_id:
                    raise ValueError("client_message_id belongs to another conversation")
                return existing
        raise


async def delete_message(db: AsyncSession, message_id: int) -> bool:
    db_message = await get_message_by_id(db, message_id)
    if not db_message:
        return False
    await remove_message(db, db_message)
    await db.commit()
    return True
