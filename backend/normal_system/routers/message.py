"""提供群聊消息写入、历史查询和删除的 HTTP 入口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from common.dependencies import get_current_user_id
from common.normal_database import get_db
from normal_system.schemas import MessageCreate, MessageInDB, PaginatedMessagesResponse
from normal_system.repositories import (
    get_message_by_id,
    get_messages_page_by_room,
    serialize_message,
)
from normal_system.services.message import create_message, delete_message

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageInDB, status_code=status.HTTP_201_CREATED)
async def create_new_message(
    message: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """以登录用户身份提交群聊消息，并返回已存储的消息。"""
    try:
        db_message = await create_message(db, message, user_id)
        return serialize_message(db_message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/room/{room_id}",
    response_model=List[MessageInDB],
    dependencies=[Depends(get_current_user_id)],
)
async def get_messages_in_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=30),
    before_id: int | None = Query(default=None, ge=1),
):
    """按消息 ID 游标返回房间的一页消息列表。"""
    items, _has_more, _next_before_id = await get_messages_page_by_room(
        db, room_id, limit=limit, before_id=before_id
    )
    return items


@router.get(
    "/room/{room_id}/page",
    response_model=PaginatedMessagesResponse,
    dependencies=[Depends(get_current_user_id)],
)
async def get_messages_page(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=30),
    before_id: int | None = Query(default=None, ge=1),
):
    """返回群聊消息页及是否还有历史、后续游标。"""
    items, has_more, next_before_id = await get_messages_page_by_room(
        db, room_id, limit=limit, before_id=before_id
    )
    return PaginatedMessagesResponse(
        items=items,
        has_more=has_more,
        next_before_id=next_before_id,
    )


@router.get(
    "/{message_id}",
    response_model=MessageInDB,
    dependencies=[Depends(get_current_user_id)],
)
async def get_single_message(message_id: int, db: AsyncSession = Depends(get_db)):
    """按 ID 返回单条群聊消息，不存在时返回 HTTP 404。"""
    message = await get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return serialize_message(message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_message(
    message_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """由作者或所属房主删除普通消息，拒绝匿名、越权和系统消息删除。"""
    try:
        success = await delete_message(db, message_id, requester_id=user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
