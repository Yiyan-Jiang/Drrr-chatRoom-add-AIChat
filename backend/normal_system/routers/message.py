from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from common.dependencies import get_current_user_id
from common.normal_database import async_session
from normal_system.schemas import MessageCreate, MessageInDB, PaginatedMessagesResponse
from normal_system.repositories import (
    create_message,
    get_message_by_id,
    get_messages_page_by_room,
    delete_message,
    serialize_message,
)

router = APIRouter(prefix="/messages", tags=["messages"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/", response_model=MessageInDB, status_code=status.HTTP_201_CREATED)
async def create_new_message(
    message: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        db_message = await create_message(db, message, user_id)
        return serialize_message(db_message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/room/{room_id}", response_model=List[MessageInDB])
async def get_messages_in_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=30),
    before_id: int | None = Query(default=None, ge=1),
):
    items, _has_more, _next_before_id = await get_messages_page_by_room(
        db, room_id, limit=limit, before_id=before_id
    )
    return items


@router.get("/room/{room_id}/page", response_model=PaginatedMessagesResponse)
async def get_messages_page(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=30),
    before_id: int | None = Query(default=None, ge=1),
):
    items, has_more, next_before_id = await get_messages_page_by_room(
        db, room_id, limit=limit, before_id=before_id
    )
    return PaginatedMessagesResponse(
        items=items,
        has_more=has_more,
        next_before_id=next_before_id,
    )


@router.get("/{message_id}", response_model=MessageInDB)
async def get_single_message(message_id: int, db: AsyncSession = Depends(get_db)):
    message = await get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return serialize_message(message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_message(message_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
