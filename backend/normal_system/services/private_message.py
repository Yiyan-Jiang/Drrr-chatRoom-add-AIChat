"""校验好友关系并提交可按客户端消息标识重放的私聊消息。"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import PrivateMessage
from normal_system.repositories.friend import get_friendship
from normal_system.repositories.private_message import (
    add_private_message,
    get_private_message_by_client_message_id,
)


async def create_private_message(
    db: AsyncSession,
    sender_id: int,
    recipient_id: int,
    content: str,
    client_message_id: str | None = None,
) -> PrivateMessage:
    """校验好友关系后提交私聊，并处理同一消息的重放。

    Args:
        db: 本次写事务使用的数据库会话。
        sender_id: 当前发送者 ID。
        recipient_id: 接收者 ID，必须与发送者存在好友关系。
        content: 私聊正文，入库前去除首尾空白。
        client_message_id: 可选客户端消息标识，用于重复发送时返回原记录。

    Returns:
        已持久化的新消息或同一发送方向的原消息。

    Raises:
        PermissionError: 双方不是好友。
        ValueError: 客户端消息标识已经属于其他会话。
        IntegrityError: 无法确认为消息重放的数据库完整性错误。
    """
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
            existing = await get_private_message_by_client_message_id(
                db, client_message_id
            )
            if existing:
                if (
                    existing.sender_id != sender_id
                    or existing.recipient_id != recipient_id
                ):
                    raise ValueError(
                        "client_message_id belongs to another conversation"
                    )
                return existing
        raise
