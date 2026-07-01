from datetime import datetime

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import FriendRequest, Friendship, PrivateMessage, User
from normal_system.schemas.friend import (
    FriendInDB,
    FriendRequestInDB,
    PaginatedFriendRequestsResponse,
    PaginatedFriendsResponse,
    PaginatedPrivateMessagesResponse,
    PrivateMessageInDB,
)


def _friend_pair(user_id: int, friend_id: int) -> tuple[int, int]:
    return (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)


def _serialize_request(request: FriendRequest, requester: User, recipient: User) -> FriendRequestInDB:
    return FriendRequestInDB(
        id=request.id,
        requester=requester,
        recipient=recipient,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


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


async def get_friendship(db: AsyncSession, user_id: int, friend_id: int) -> Friendship | None:
    low_id, high_id = _friend_pair(user_id, friend_id)
    res = await db.execute(
        select(Friendship).where(
            Friendship.user_low_id == low_id,
            Friendship.user_high_id == high_id,
        )
    )
    return res.scalar_one_or_none()


async def create_friend_request(db: AsyncSession, requester_id: int, recipient_id: int) -> FriendRequest:
    if requester_id == recipient_id:
        raise ValueError("Cannot friend yourself")
    if await get_friendship(db, requester_id, recipient_id):
        raise ValueError("Users are already friends")

    res = await db.execute(
        select(FriendRequest).where(
            FriendRequest.requester_id == requester_id,
            FriendRequest.recipient_id == recipient_id,
            FriendRequest.status == "pending",
        )
    )
    if res.scalar_one_or_none():
        raise ValueError("pending request already exists")

    request = FriendRequest(
        requester_id=requester_id,
        recipient_id=recipient_id,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def accept_friend_request(db: AsyncSession, request_id: int, recipient_id: int) -> FriendRequest:
    res = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    request = res.scalar_one_or_none()
    if not request:
        raise ValueError("Friend request not found")
    if request.recipient_id != recipient_id:
        raise PermissionError("Only recipient can accept this request")
    if request.status != "pending":
        raise ValueError("Friend request is not pending")

    low_id, high_id = _friend_pair(request.requester_id, request.recipient_id)
    friendship = await get_friendship(db, request.requester_id, request.recipient_id)
    if friendship is None:
        db.add(Friendship(user_low_id=low_id, user_high_id=high_id, created_at=datetime.now()))
    request.status = "accepted"
    request.updated_at = datetime.now()
    await db.commit()
    await db.refresh(request)
    return request


async def reject_friend_request(db: AsyncSession, request_id: int, recipient_id: int) -> FriendRequest:
    return await _update_request_status(db, request_id, recipient_id, "rejected", role="recipient")


async def cancel_friend_request(db: AsyncSession, request_id: int, requester_id: int) -> FriendRequest:
    return await _update_request_status(db, request_id, requester_id, "canceled", role="requester")


async def _update_request_status(
    db: AsyncSession,
    request_id: int,
    actor_id: int,
    status: str,
    role: str,
) -> FriendRequest:
    res = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    request = res.scalar_one_or_none()
    if not request:
        raise ValueError("Friend request not found")
    expected_id = request.recipient_id if role == "recipient" else request.requester_id
    if expected_id != actor_id:
        raise PermissionError(f"Only {role} can update this request")
    if request.status != "pending":
        raise ValueError("Friend request is not pending")
    request.status = status
    request.updated_at = datetime.now()
    await db.commit()
    await db.refresh(request)
    return request


async def list_friend_requests(
    db: AsyncSession,
    user_id: int,
    direction: str = "all",
) -> PaginatedFriendRequestsResponse:
    filters = []
    if direction == "incoming":
        filters.append(FriendRequest.recipient_id == user_id)
    elif direction == "outgoing":
        filters.append(FriendRequest.requester_id == user_id)
    else:
        filters.append(or_(FriendRequest.requester_id == user_id, FriendRequest.recipient_id == user_id))

    requester_user = aliased(User)
    recipient_user = aliased(User)
    res = await db.execute(
        select(FriendRequest, requester_user, recipient_user)
        .join(requester_user, FriendRequest.requester_id == requester_user.id)
        .join(recipient_user, FriendRequest.recipient_id == recipient_user.id)
        .where(*filters)
        .order_by(FriendRequest.updated_at.desc(), FriendRequest.id.desc())
    )
    items = [_serialize_request(request, requester, recipient) for request, requester, recipient in res.all()]
    return PaginatedFriendRequestsResponse(items=items)


async def list_friends(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedFriendsResponse:
    safe_page = max(1, page)
    safe_page_size = max(1, min(page_size, 50))
    offset = (safe_page - 1) * safe_page_size

    relation_filter = or_(Friendship.user_low_id == user_id, Friendship.user_high_id == user_id)
    total_res = await db.execute(select(func.count()).select_from(Friendship).where(relation_filter))
    total = total_res.scalar_one()

    res = await db.execute(
        select(Friendship, User)
        .join(
            User,
            or_(
                and_(Friendship.user_low_id == user_id, User.id == Friendship.user_high_id),
                and_(Friendship.user_high_id == user_id, User.id == Friendship.user_low_id),
            ),
        )
        .where(relation_filter)
        .order_by(Friendship.created_at.desc(), Friendship.id.desc())
        .offset(offset)
        .limit(safe_page_size)
    )
    items = [FriendInDB(user=user, created_at=friendship.created_at) for friendship, user in res.all()]
    return PaginatedFriendsResponse(
        items=items,
        total=total,
        page=safe_page,
        page_size=safe_page_size,
        has_more=offset + len(items) < total,
    )


async def delete_friendship(db: AsyncSession, user_id: int, friend_id: int) -> bool:
    friendship = await get_friendship(db, user_id, friend_id)
    if not friendship:
        return False
    await db.execute(
        delete(PrivateMessage).where(
            or_(
                and_(PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id == friend_id),
                and_(PrivateMessage.sender_id == friend_id, PrivateMessage.recipient_id == user_id),
            )
        )
    )
    await db.delete(friendship)
    await db.commit()
    return True


async def get_private_message_by_client_message_id(
    db: AsyncSession,
    client_message_id: str,
) -> PrivateMessage | None:
    res = await db.execute(select(PrivateMessage).where(PrivateMessage.client_message_id == client_message_id))
    return res.scalar_one_or_none()


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
            return existing

    message = PrivateMessage(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content.strip(),
        client_message_id=client_message_id,
        created_at=datetime.now(),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
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
