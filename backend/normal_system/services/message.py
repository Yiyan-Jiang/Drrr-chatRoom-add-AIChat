"""提交群聊消息写事务并按客户端消息标识处理重放。"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import Message
from normal_system.repositories.message import (
    add_message,
    get_message_by_client_message_id,
    get_message_by_id,
    remove_message,
)
from normal_system.repositories.room import get_room_by_id
from normal_system.schemas import MessageCreate


async def create_message(
    db: AsyncSession,
    message: MessageCreate,
    user_id: int | None,
    message_type: str = "user",
) -> Message:
    """提交群聊消息，重复客户端消息标识返回原记录。

    Args:
        db: 本次操作独立使用的数据库会话，由此服务提交写事务。
        message: 消息正文、所属房间及可选客户端消息标识。
        user_id: 消息发送者 ID，可为空以保留无作者消息。
        message_type: 用户消息或系统消息类型。

    Returns:
        已持久化的新消息，或同一用户在同一房间先前提交的消息。

    Raises:
        ValueError: 房间不存在，或客户端消息标识属于其他会话。
        IntegrityError: 回滚后仍不能确认为同一消息重放的完整性错误。
    """
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
            existing = await get_message_by_client_message_id(
                db, message.client_message_id
            )
            if existing:
                if existing.user_id != user_id or existing.room_id != message.room_id:
                    raise ValueError(
                        "client_message_id belongs to another conversation"
                    )
                return existing
        raise


async def delete_message(db: AsyncSession, message_id: int) -> bool:
    """删除已有群聊消息并提交事务，不存在时返回 False。"""
    db_message = await get_message_by_id(db, message_id)
    if not db_message:
        return False
    await remove_message(db, db_message)
    await db.commit()
    return True
