from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from common.dependencies import get_current_user_id
from common.normal_database import async_session
from normal_system.schemas import RoomCreate, RoomInDB, RoomOwner, RoomUpdate, RoomWithMessages
from normal_system.repositories import (
    create_room,
    get_user_by_id,
    get_room_by_id,
    get_room_by_name,
    delete_room,
    get_message_by_room,
    get_all_rooms,
    get_rooms_by_owner,
    update_room,
)
from normal_system.routers.socket import room_presence, sio

router = APIRouter(prefix="/rooms", tags=["rooms"])


async def get_db():
    async with async_session() as session:
        yield session


async def _to_room_response(db: AsyncSession, room) -> RoomInDB:
    owner = await get_user_by_id(db, room.owner_id) if room.owner_id else None
    return RoomInDB(
        id=room.id,
        name=room.name,
        description=room.description or "",
        notice=room.notice or "",
        rules=room.rules or "",
        tags=room.tags or [],
        min_age=room.min_age,
        max_age=room.max_age,
        max_members=room.max_members,
        peak_online_members=room.peak_online_members,
        online_members=room_presence.count(room.id),
        owner_id=room.owner_id,
        owner=RoomOwner.model_validate(owner) if owner else None,
        created_at=room.created_at,
    )


@router.post("/", response_model=RoomInDB, status_code=status.HTTP_201_CREATED)
async def create_new_room(
        room: RoomCreate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    try:
        db_room = await create_room(db, room, owner_id=user_id)
        owner = await get_user_by_id(db, user_id)
        return RoomInDB(
            id=db_room.id,
            name=db_room.name,
            description=db_room.description or "",
            notice=db_room.notice or "",
            rules=db_room.rules or "",
            tags=db_room.tags or [],
            min_age=db_room.min_age,
            max_age=db_room.max_age,
            max_members=db_room.max_members,
            peak_online_members=db_room.peak_online_members,
            online_members=room_presence.count(db_room.id),
            owner_id=db_room.owner_id,
            owner=RoomOwner.model_validate(owner) if owner else None,
            created_at=db_room.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[RoomInDB])
async def list_rooms(
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0, description="跳过多少条"),
        limit: int = Query(50, ge=1, le=200, description="最多返回多少条"),
):
    rooms = await get_all_rooms(db, skip=skip, limit=limit)
    return [await _to_room_response(db, room) for room in rooms]


@router.get("/mine", response_model=List[RoomInDB])
async def list_my_rooms(
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    rooms = await get_rooms_by_owner(db, owner_id=user_id)
    return [await _to_room_response(db, room) for room in rooms]


@router.get("/viewers/count")
async def get_room_viewer_count():
    return {"total": room_presence.total_viewers()}


@router.get("/name/{name}", response_model=RoomInDB)
async def get_room_by_name_endpoint(name: str, db: AsyncSession = Depends(get_db)):
    room = await get_room_by_name(db, name)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    owner = await get_user_by_id(db, room.owner_id) if room.owner_id else None
    return RoomInDB(
        id=room.id,
        name=room.name,
        description=room.description or "",
        notice=room.notice or "",
        rules=room.rules or "",
        tags=room.tags or [],
        min_age=room.min_age,
        max_age=room.max_age,
        max_members=room.max_members,
        peak_online_members=room.peak_online_members,
        online_members=room_presence.count(room.id),
        owner_id=room.owner_id,
        owner=RoomOwner.model_validate(owner) if owner else None,
        created_at=room.created_at,
    )


@router.get("/{room_id:int}", response_model=RoomWithMessages)
async def get_room_detail(room_id: int, db: AsyncSession = Depends(get_db)):
    room = await get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    messages = await get_message_by_room(db, room_id)
    owner = await get_user_by_id(db, room.owner_id) if room.owner_id else None

    return RoomWithMessages(
        id=room_id,
        name=room.name,
        description=room.description or "",
        notice=room.notice or "",
        rules=room.rules or "",
        tags=room.tags or [],
        min_age=room.min_age,
        max_age=room.max_age,
        max_members=room.max_members,
        peak_online_members=room.peak_online_members,
        online_members=room_presence.count(room_id),
        owner_id=room.owner_id,
        owner=RoomOwner.model_validate(owner) if owner else None,
        messages=messages,
        created_at=room.created_at,
    )


@router.patch("/{room_id:int}")
async def update_existing_room(
        room_id: int,
        room_update: RoomUpdate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    try:
        updated = await update_room(db, room_id, room_update, requester_id=user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return updated


@router.delete("/{room_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_room(
        room_id: int,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    try:
        success = await delete_room(db, room_id, requester_id=user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    room_presence.clear_room(room_id)
    await sio.emit("room_deleted", {"room_id": room_id}, room=f"room_{room_id}")
