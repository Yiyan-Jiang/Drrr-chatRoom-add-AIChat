"""提供好友申请、好友关系和私聊历史的 HTTP 入口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.dependencies import get_current_user_id
from common.normal_database import get_db
from normal_system.services.friend import (
    accept_friend_request,
    cancel_friend_request,
    create_friend_request,
    delete_friendship,
    reject_friend_request,
)
from normal_system.repositories.friend import list_friend_requests, list_friends
from normal_system.repositories.private_message import list_private_messages
from normal_system.schemas import (
    FriendRequestCreate,
    FriendRequestInDB,
    PaginatedFriendRequestsResponse,
    PaginatedFriendsResponse,
    PaginatedPrivateMessagesResponse,
)

router = APIRouter(prefix="/friends", tags=["friends"])
private_message_router = APIRouter(
    prefix="/private-messages", tags=["private-messages"]
)


@router.get("/", response_model=PaginatedFriendsResponse)
async def list_friends_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """返回当前登录用户的分页好友列表。"""
    return await list_friends(db, user_id=user_id, page=page, page_size=page_size)


@router.post(
    "/requests", response_model=FriendRequestInDB, status_code=status.HTTP_201_CREATED
)
async def create_friend_request_endpoint(
    payload: FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """提交好友申请并返回包含双方公开资料的申请记录。"""
    try:
        request = await create_friend_request(
            db, requester_id=user_id, recipient_id=payload.recipient_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    page = await list_friend_requests(db, user_id=user_id, direction="outgoing")
    return next(item for item in page.items if item.id == request.id)


@router.get("/requests", response_model=PaginatedFriendRequestsResponse)
async def list_friend_requests_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    direction: str = Query("all", pattern="^(incoming|outgoing|all)$"),
):
    """按收件、发件或全部方向返回当前用户的好友申请。"""
    return await list_friend_requests(db, user_id=user_id, direction=direction)


@router.post("/requests/{request_id:int}/accept", response_model=FriendRequestInDB)
async def accept_friend_request_endpoint(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """接受当前用户收到的申请，并返回更新后的记录。"""
    try:
        request = await accept_friend_request(db, request_id, recipient_id=user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    page = await list_friend_requests(db, user_id=user_id, direction="incoming")
    return next(item for item in page.items if item.id == request.id)


@router.post("/requests/{request_id:int}/reject", response_model=FriendRequestInDB)
async def reject_friend_request_endpoint(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """拒绝当前用户收到的申请，并返回更新后的记录。"""
    try:
        request = await reject_friend_request(db, request_id, recipient_id=user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    page = await list_friend_requests(db, user_id=user_id, direction="incoming")
    return next(item for item in page.items if item.id == request.id)


@router.post("/requests/{request_id:int}/cancel", response_model=FriendRequestInDB)
async def cancel_friend_request_endpoint(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """取消当前用户发出的申请，并返回更新后的记录。"""
    try:
        request = await cancel_friend_request(db, request_id, requester_id=user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    page = await list_friend_requests(db, user_id=user_id, direction="outgoing")
    return next(item for item in page.items if item.id == request.id)


@router.delete("/{friend_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_friend_endpoint(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """删除当前用户与指定好友的关系及私聊，不存在时返回 HTTP 404。"""
    deleted = await delete_friendship(db, user_id=user_id, friend_id=friend_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found"
        )


@private_message_router.get(
    "/{friend_id:int}", response_model=PaginatedPrivateMessagesResponse
)
async def list_private_messages_endpoint(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    before_id: int | None = Query(default=None, ge=1),
):
    """按消息游标返回当前用户与指定用户的私聊历史。"""
    return await list_private_messages(
        db, user_id=user_id, friend_id=friend_id, limit=limit, before_id=before_id
    )
