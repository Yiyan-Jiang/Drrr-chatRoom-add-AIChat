from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import PrivateMessage
from normal_system.repositories.friend import get_friendship
from normal_system.repositories.private_message import add_private_message, get_private_message_by_client_message_id


async def create_private_message(
    db: AsyncSession,
    sender_id: int,
    recipient_id: int,
    content: str,
    client_message_id: str | None = None,
) -> PrivateMessage:
    if not await get_friendship(db, sender_id, recipient_id):
        raise PermissionError("Only friends can send private messages")
    if client_message_id:
        existing = await get_private_message_by_client_message_id(db, client_message_id)
        if existing:
            if existing.sender_id != sender_id or existing.recipient_id != recipient_id:
                raise ValueError("client_message_id belongs to another conversation")
            return existing

    message = add_private_message(
        db,
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content.strip(),
        client_message_id=client_message_id,
        created_at=datetime.now(),
    )
    try:
        await db.commit()
        await db.refresh(message)
        return message
    except IntegrityError:
        await db.rollback()
        if client_message_id:
            existing = await get_private_message_by_client_message_id(db, client_message_id)
            if existing:
                if existing.sender_id != sender_id or existing.recipient_id != recipient_id:
                    raise ValueError("client_message_id belongs to another conversation")
                return existing
        raise
