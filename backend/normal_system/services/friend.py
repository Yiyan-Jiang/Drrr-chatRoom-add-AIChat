from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import FriendRequest
from normal_system.repositories.friend import (
    add_friend_request,
    add_friendship,
    get_friend_request_by_id,
    get_friendship,
    get_pending_friend_request,
    remove_friendship_and_messages,
    set_friend_request_status,
)


async def create_friend_request(db: AsyncSession, requester_id: int, recipient_id: int) -> FriendRequest:
    if requester_id == recipient_id:
        raise ValueError("Cannot friend yourself")
    if await get_friendship(db, requester_id, recipient_id):
        raise ValueError("Users are already friends")

    if await get_pending_friend_request(db, requester_id, recipient_id):
        raise ValueError("pending request already exists")

    request = add_friend_request(
        db,
        requester_id=requester_id,
        recipient_id=recipient_id,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    await db.commit()
    await db.refresh(request)
    return request


async def accept_friend_request(db: AsyncSession, request_id: int, recipient_id: int) -> FriendRequest:
    request = await get_friend_request_by_id(db, request_id)
    if not request:
        raise ValueError("Friend request not found")
    if request.recipient_id != recipient_id:
        raise PermissionError("Only recipient can accept this request")
    if request.status != "pending":
        raise ValueError("Friend request is not pending")

    friendship = await get_friendship(db, request.requester_id, request.recipient_id)
    if friendship is None:
        add_friendship(db, request.requester_id, request.recipient_id, created_at=datetime.now())
    set_friend_request_status(request, "accepted", updated_at=datetime.now())
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
    request = await get_friend_request_by_id(db, request_id)
    if not request:
        raise ValueError("Friend request not found")
    expected_id = request.recipient_id if role == "recipient" else request.requester_id
    if expected_id != actor_id:
        raise PermissionError(f"Only {role} can update this request")
    if request.status != "pending":
        raise ValueError("Friend request is not pending")
    set_friend_request_status(request, status, updated_at=datetime.now())
    await db.commit()
    await db.refresh(request)
    return request


async def delete_friendship(db: AsyncSession, user_id: int, friend_id: int) -> bool:
    friendship = await get_friendship(db, user_id, friend_id)
    if not friendship:
        return False
    await remove_friendship_and_messages(db, friendship, user_id, friend_id)
    await db.commit()
    return True
