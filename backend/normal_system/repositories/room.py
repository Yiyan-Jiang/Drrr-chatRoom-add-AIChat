"""读写房间模型，事务由业务服务管理。"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from normal_system.models import Room


async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    """按房间 ID 读取房间，不存在时返回 None。"""
    res = await db.execute(select(Room).filter(Room.id == room_id))
    return res.scalar_one_or_none()


async def get_room_by_name(db: AsyncSession, name: str) -> Optional[Room]:
    """按房间名称读取房间，不存在时返回 None。"""
    res = await db.execute(select(Room).filter(Room.name == name))
    return res.scalar_one_or_none()


def add_room(db: AsyncSession, *, created_at: datetime, **fields) -> Room:
    """把房间与创建时间加入会话，不提交事务。"""
    room = Room(**fields, created_at=created_at)
    db.add(room)
    return room


async def get_all_rooms(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Room]:
    """按创建时间倒序及偏移量读取房间列表。"""
    res = await db.execute(
        select(Room).order_by(Room.created_at.desc()).offset(skip).limit(limit)
    )
    return res.scalars().all()


async def get_rooms_by_owner(db: AsyncSession, owner_id: int) -> List[Room]:
    """按创建时间倒序读取指定房主的全部房间。"""
    res = await db.execute(
        select(Room).where(Room.owner_id == owner_id).order_by(Room.created_at.desc())
    )
    return res.scalars().all()


def set_room_fields(room: Room, fields: dict) -> None:
    """按调用方给出的字段更新房间模型，不提交事务。"""
    for field, value in fields.items():
        setattr(room, field, value)


async def remove_room(db: AsyncSession, room: Room) -> None:
    """在会话中标记删除房间，不提交事务。"""
    await db.delete(room)
