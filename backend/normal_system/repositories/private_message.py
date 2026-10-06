from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import PrivateMessage, User
from normal_system.schemas.friend import PaginatedPrivateMessagesResponse, PrivateMessageInDB


def _serialize_private_message(message: PrivateMessage, author: User) -> PrivateMessageInDB:
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
    res = await db.execute(select(PrivateMessage).where(PrivateMessage.client_message_id == client_message_id))
    return res.scalar_one_or_none()


def add_private_message(db: AsyncSession, **fields) -> PrivateMessage:
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
    safe_limit = max(1, min(limit, 50))
    filters = [
        or_(
            and_(PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id == friend_id),
            and_(PrivateMessage.sender_id == friend_id, PrivateMessage.recipient_id == user_id),
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
    items = [_serialize_private_message(message, author) for message, author in page_rows]
    return PaginatedPrivateMessagesResponse(
        items=items,
        has_more=has_more,
        next_before_id=items[-1].id if has_more and items else None,
    )
