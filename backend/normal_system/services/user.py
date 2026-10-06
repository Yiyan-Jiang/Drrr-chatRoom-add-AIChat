import hashlib
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from common.passwords import hash_password
from normal_system.models import User
from normal_system.repositories.user import (
    add_user,
    get_user_by_id,
    remove_user_and_owned_rooms,
    set_user_profile,
)
from normal_system.schemas import UserCreate, UserProfileUpdate, UserUpdate
from tool.isUnion_name import is_duplicate_entry_error


AVATAR_KEYS = ("admin", "gray", "kanra", "pink", "setton", "tanaka", "zaika", "zawa")


def _default_avatar_key(username: str) -> str:
    digest = hashlib.sha256(username.encode("utf-8")).digest()
    return AVATAR_KEYS[digest[0] % len(AVATAR_KEYS)]


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = await run_in_threadpool(hash_password, user.password)
    db_user = add_user(
        db,
        username=user.username,
        password=hashed_password,
        nickname=user.username,
        bio="",
        avatar_key=_default_avatar_key(user.username),
    )
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_entry_error(e, "username"):
            raise ValueError(f"User {user.username} already exists")
        raise


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
    requester_id: int | None = None,
) -> Optional[User]:
    if requester_id is not None and user_id != requester_id:
        raise PermissionError("Cannot update another user")
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    set_user_profile(
        db_user,
        nickname=user_update.nickname,
        bio=user_update.bio,
        avatar_key=user_update.avatar_key,
    )
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise


async def update_user_profile(
    db: AsyncSession,
    user_id: int,
    profile: UserProfileUpdate,
) -> Optional[User]:
    return await update_user(
        db,
        user_id,
        UserUpdate(nickname=profile.nickname, bio=profile.bio, avatar_key=profile.avatar_key),
    )


async def delete_user(db: AsyncSession, user_id: int, requester_id: int | None = None) -> bool:
    if requester_id is not None and user_id != requester_id:
        raise PermissionError("Cannot delete another user")
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    await remove_user_and_owned_rooms(db, db_user, user_id)
    await db.commit()
    return True
