"""查询用户并登记账号及关联资源变更，不提交事务。"""

from typing import Optional

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from normal_system.models import Message, Room, User


async def get_user_count(db: AsyncSession) -> int:
    """查询当前账号总数。"""
    res = await db.execute(select(func.count()).select_from(User))
    return res.scalar_one()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """按用户 ID 读取账号，不存在时返回 None。"""
    res = await db.execute(select(User).filter(User.id == user_id))
    return res.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """按用户名读取账号，不存在时返回 None。"""
    res = await db.execute(select(User).filter(User.username == username))
    return res.scalar_one_or_none()


def add_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    nickname: str,
    bio: str,
    avatar_key: str,
) -> User:
    """将包含密码摘要的账号加入会话，不提交事务。"""
    user = User(
        username=username,
        password=password,
        nickname=nickname,
        bio=bio,
        avatar_key=avatar_key,
    )
    db.add(user)
    return user


def set_user_profile(
    user: User, *, nickname: str, bio: str, avatar_key: str | None
) -> None:
    """更新昵称与简介，仅在提供头像键时替换头像，不提交事务。"""
    user.nickname = nickname
    user.bio = bio
    if avatar_key is not None:
        user.avatar_key = avatar_key


def set_user_password(user: User, password: str) -> None:
    """替换账号的密码摘要，不提交事务。"""
    user.password = password


async def remove_user_and_owned_rooms(
    db: AsyncSession, user: User, user_id: int
) -> None:
    """删除用户创建的房间及房间消息，再标记删除账号，不提交事务。"""
    owned_room_ids = select(Room.id).where(Room.owner_id == user_id)
    await db.execute(delete(Message).where(Message.room_id.in_(owned_room_ids)))
    await db.execute(delete(Room).where(Room.owner_id == user_id))
    await db.delete(user)
