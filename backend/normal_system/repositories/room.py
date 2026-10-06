from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from normal_system.models import Room


async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    res = await db.execute(select(Room).filter(Room.id == room_id))
    return res.scalar_one_or_none()


async def get_room_by_name(db: AsyncSession, name: str) -> Optional[Room]:
    res = await db.execute(select(Room).filter(Room.name == name))
    return res.scalar_one_or_none()


def add_room(db: AsyncSession, *, created_at: datetime, **fields) -> Room:
    room = Room(**fields, created_at=created_at)
    db.add(room)
    return room


async def get_all_rooms(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Room]:
    res = await db.execute(select(Room).order_by(Room.created_at.desc()).offset(skip).limit(limit))
    return res.scalars().all()


async def get_rooms_by_owner(db: AsyncSession, owner_id: int) -> List[Room]:
    res = await db.execute(select(Room).where(Room.owner_id == owner_id).order_by(Room.created_at.desc()))
    return res.scalars().all()


def set_room_fields(room: Room, fields: dict) -> None:
    for field, value in fields.items():
        setattr(room, field, value)


async def remove_room(db: AsyncSession, room: Room) -> None:
    await db.delete(room)
