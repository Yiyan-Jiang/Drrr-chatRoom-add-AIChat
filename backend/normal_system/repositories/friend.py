"""读写好友申请、好友关系及关联私聊数据，不提交事务。"""

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
)


def _friend_pair(user_id: int, friend_id: int) -> tuple[int, int]:
    """将两个用户 ID 排为低位、高位，供无向好友关系查询使用。"""
    return (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)


def _serialize_request(
    request: FriendRequest, requester: User, recipient: User
) -> FriendRequestInDB:
    """将申请记录与申请双方的公开资料组合为响应模型。"""
    return FriendRequestInDB(
        id=request.id,
        requester=requester,
        recipient=recipient,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


async def get_friendship(
    db: AsyncSession, user_id: int, friend_id: int
) -> Friendship | None:
    """按无向用户对读取好友关系，不存在时返回 None。"""
    low_id, high_id = _friend_pair(user_id, friend_id)
    res = await db.execute(
        select(Friendship).where(
            Friendship.user_low_id == low_id,
            Friendship.user_high_id == high_id,
        )
    )
    return res.scalar_one_or_none()


async def list_friend_requests(
    db: AsyncSession,
    user_id: int,
    direction: str = "all",
) -> PaginatedFriendRequestsResponse:
    """按申请方向读取当前用户的全部申请，按最近更新时间排序。"""
    filters = []
    if direction == "incoming":
        filters.append(FriendRequest.recipient_id == user_id)
    elif direction == "outgoing":
        filters.append(FriendRequest.requester_id == user_id)
    else:
        filters.append(
            or_(
                FriendRequest.requester_id == user_id,
                FriendRequest.recipient_id == user_id,
            )
        )

    requester_user = aliased(User)
    recipient_user = aliased(User)
    res = await db.execute(
        select(FriendRequest, requester_user, recipient_user)
        .join(requester_user, FriendRequest.requester_id == requester_user.id)
        .join(recipient_user, FriendRequest.recipient_id == recipient_user.id)
        .where(*filters)
        .order_by(FriendRequest.updated_at.desc(), FriendRequest.id.desc())
    )
    items = [
        _serialize_request(request, requester, recipient)
        for request, requester, recipient in res.all()
    ]
    return PaginatedFriendRequestsResponse(items=items)


async def list_friends(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedFriendsResponse:
    """按页码读取好友资料及关系创建时间，同时返回总数。"""
    safe_page = max(1, page)
    safe_page_size = max(1, min(page_size, 50))
    offset = (safe_page - 1) * safe_page_size

    relation_filter = or_(
        Friendship.user_low_id == user_id, Friendship.user_high_id == user_id
    )
    total_res = await db.execute(
        select(func.count()).select_from(Friendship).where(relation_filter)
    )
    total = total_res.scalar_one()

    res = await db.execute(
        select(Friendship, User)
        .join(
            User,
            or_(
                and_(
                    Friendship.user_low_id == user_id,
                    User.id == Friendship.user_high_id,
                ),
                and_(
                    Friendship.user_high_id == user_id,
                    User.id == Friendship.user_low_id,
                ),
            ),
        )
        .where(relation_filter)
        .order_by(Friendship.created_at.desc(), Friendship.id.desc())
        .offset(offset)
        .limit(safe_page_size)
    )
    items = [
        FriendInDB(user=user, created_at=friendship.created_at)
        for friendship, user in res.all()
    ]
    return PaginatedFriendsResponse(
        items=items,
        total=total,
        page=safe_page,
        page_size=safe_page_size,
        has_more=offset + len(items) < total,
    )


async def get_pending_friend_request(
    db: AsyncSession, requester_id: int, recipient_id: int
) -> FriendRequest | None:
    """读取指定申请方向的待处理申请，不存在时返回 None。"""
    res = await db.execute(
        select(FriendRequest).where(
            FriendRequest.requester_id == requester_id,
            FriendRequest.recipient_id == recipient_id,
            FriendRequest.status == "pending",
        )
    )
    return res.scalar_one_or_none()


async def get_friend_request_by_id(
    db: AsyncSession, request_id: int
) -> FriendRequest | None:
    """读取好友申请记录，不存在时返回 None。"""
    res = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    return res.scalar_one_or_none()


def add_friend_request(db: AsyncSession, **fields) -> FriendRequest:
    """把好友申请加入会话，不提交事务。"""
    request = FriendRequest(**fields)
    db.add(request)
    return request


def add_friendship(
    db: AsyncSession, user_id: int, friend_id: int, *, created_at: datetime
) -> Friendship:
    """按排序后的用户对登记好友关系，不提交事务。"""
    low_id, high_id = _friend_pair(user_id, friend_id)
    friendship = Friendship(
        user_low_id=low_id, user_high_id=high_id, created_at=created_at
    )
    db.add(friendship)
    return friendship


def set_friend_request_status(
    request: FriendRequest, status: str, *, updated_at: datetime
) -> None:
    """修改申请的状态与更新时间，不提交事务。"""
    request.status = status
    request.updated_at = updated_at


async def remove_friendship_and_messages(
    db: AsyncSession, friendship: Friendship, user_id: int, friend_id: int
) -> None:
    """删除两人私聊及好友关系，事务由调用方提交。"""
    await db.execute(
        delete(PrivateMessage).where(
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
        )
    )
    await db.delete(friendship)
