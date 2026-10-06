from datetime import datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import Room
from normal_system.repositories.message import delete_messages_by_room
from normal_system.repositories.room import add_room, get_room_by_id, remove_room, set_room_fields
from normal_system.schemas import RoomCreate, RoomUpdate
from tool.isUnion_name import is_duplicate_entry_error


async def create_room(db: AsyncSession, room: RoomCreate, owner_id: int | None = None) -> Room:
    db_room = add_room(
        db,
        name=room.name,
        description=room.description,
        notice=room.notice,
        rules=room.rules,
        tags=room.tags,
        min_age=room.min_age,
        max_age=room.max_age,
        max_members=room.max_members,
        peak_online_members=1,
        owner_id=owner_id,
        created_at=datetime.now(),
    )
    try:
        await db.commit()
        await db.refresh(db_room)
        return db_room
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_entry_error(e, "name"):
            raise ValueError(f"Room {room.name} already exists")
        raise


async def update_room(
    db: AsyncSession,
    room_id: int,
    room_update: RoomUpdate,
    requester_id: int,
) -> Optional[dict]:
    db_room = await get_room_by_id(db, room_id)
    if not db_room:
        return None
    if db_room.owner_id != requester_id:
        raise PermissionError("Only room owner can update this room")

    payload = room_update.model_dump(exclude_unset=True)
    allowed_fields = ("name", "description", "notice", "rules")
    set_room_fields(
        db_room,
        {field: payload[field] for field in allowed_fields if field in payload and payload[field] is not None},
    )
    try:
        await db.commit()
        return {field: getattr(db_room, field) for field in allowed_fields}
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_entry_error(e, "name"):
            raise ValueError(f"Room {room_update.name} already exists")
        raise


async def update_room_peak_online_members(
    db: AsyncSession,
    room_id: int,
    online_members: int,
) -> Optional[Room]:
    db_room = await get_room_by_id(db, room_id)
    if not db_room:
        return None
    current_peak = db_room.peak_online_members or 1
    if online_members > current_peak:
        set_room_fields(db_room, {"peak_online_members": online_members})
        await db.commit()
        await db.refresh(db_room)
    return db_room


async def delete_room(
    db: AsyncSession,
    room_id: int,
    requester_id: int | None = None,
) -> bool:
    db_room = await get_room_by_id(db, room_id)
    if not db_room:
        return False
    if requester_id is not None and db_room.owner_id is not None and db_room.owner_id != requester_id:
        raise PermissionError("Only room owner can delete this room")
    await delete_messages_by_room(db, room_id)
    await remove_room(db, db_room)
    await db.commit()
    return True
