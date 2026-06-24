from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, func
from normal_system.models import User, Message, Room
from normal_system.schemas import (
    MessageInDB,
    MessageCreate,
    RoomCreate,
    RoomUpdate,
    UserCreate,
    UserProfileUpdate,
    UserPublic,
    UserUpdate,
)
from tool.isUnion_name import is_duplicate_entry_error


# User
AVATAR_KEYS = ("admin", "gray", "kanra", "pink", "setton", "tanaka", "zaika", "zawa")


def _default_avatar_key(username: str) -> str:
    digest = hashlib.sha256(username.encode("utf-8")).digest()
    return AVATAR_KEYS[digest[0] % len(AVATAR_KEYS)]


async def get_user_count(db: AsyncSession) -> int:
    res = await db.execute(select(func.count()).select_from(User))
    return res.scalar_one()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    res = await db.execute(select(User).filter(User.id == user_id))
    return res.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    res = await db.execute(select(User).filter(User.username == username))
    return res.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    # 哈希加密密码
    db_user = User(
        username=user.username,
        password=hashed_password,
        nickname=user.username,
        bio="",
        avatar_key=_default_avatar_key(user.username),
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_entry_error(e, "username"):
            raise ValueError(f"User {user.username} already exists")
        else:
            raise


async def update_user(
    db: AsyncSession, user_id: int, user_update: UserUpdate
) -> Optional[User]:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.nickname = user_update.nickname
    db_user.bio = user_update.bio
    if user_update.avatar_key is not None:
        db_user.avatar_key = user_update.avatar_key
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as e:
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
        UserUpdate(
            nickname=profile.nickname,
            bio=profile.bio,
            avatar_key=profile.avatar_key,
        ),
    )


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    owned_room_ids = select(Room.id).where(Room.owner_id == user_id)
    await db.execute(delete(Message).where(Message.room_id.in_(owned_room_ids)))
    await db.execute(delete(Room).where(Room.owner_id == user_id))
    await db.delete(db_user)
    await db.commit()
    return True


# Message
def serialize_message(message: Message, author: User | None = None) -> MessageInDB:
    return MessageInDB(
        id=message.id,
        content=message.content,
        room_id=message.room_id,
        client_message_id=message.client_message_id,
        user_id=message.user_id,
        message_type=message.message_type or "user",
        author=UserPublic.model_validate(author) if author else None,
        created_at=message.created_at,
    )


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
    res = await db.execute(select(Message).filter(Message.id == message_id))
    return res.scalar_one_or_none()


async def get_message_by_room(db: AsyncSession, room_id: int) -> List[Message]:
    res = await db.execute(
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    messages: List[Message] = res.scalars().all()
    return messages


async def get_messages_with_authors_by_room(
    db: AsyncSession,
    room_id: int,
    limit: int = 50,
) -> List[MessageInDB]:
    res = await db.execute(
        select(Message, User)
        .outerjoin(User, Message.user_id == User.id)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = res.all()
    return [serialize_message(message, author) for message, author in rows]


async def get_messages_page_by_room(
    db: AsyncSession,
    room_id: int,
    limit: int = 10,
    before_id: int | None = None,
) -> tuple[list[MessageInDB], bool, int | None]:
    safe_limit = max(1, min(limit, 30))
    filters = [Message.room_id == room_id]
    if before_id is not None:
        filters.append(Message.id < before_id)

    res = await db.execute(
        select(Message, User)
        .outerjoin(User, Message.user_id == User.id)
        .where(*filters)
        .order_by(Message.id.desc())
        .limit(safe_limit + 1)
    )
    rows = res.all()
    has_more = len(rows) > safe_limit
    page_rows = rows[:safe_limit]
    items = [serialize_message(message, author) for message, author in page_rows]
    next_before_id = items[-1].id if has_more and items else None
    return items, has_more, next_before_id


async def get_message_by_client_message_id(
    db: AsyncSession, client_message_id: str
) -> Optional[Message]:
    res = await db.execute(
        select(Message).where(Message.client_message_id == client_message_id)
    )
    return res.scalar_one_or_none()


async def create_message(
    db: AsyncSession,
    message: MessageCreate,
    user_id: int | None,
    message_type: str = "user",
) -> Message:
    room = await get_room_by_id(db, message.room_id)
    if not room:
        raise ValueError(f"Room {message.room_id} does not exist")

    if message.client_message_id:
        existing = await get_message_by_client_message_id(db, message.client_message_id)
        if existing:
            return existing

    db_message = Message(
        content=message.content,
        room_id=message.room_id,
        user_id=user_id,
        message_type=message_type,
        client_message_id=message.client_message_id,
        created_at=datetime.now(),
    )
    db.add(db_message)
    try:
        await db.commit()
        await db.refresh(db_message)
        return db_message
    except IntegrityError:
        await db.rollback()
        if message.client_message_id:
            existing = await get_message_by_client_message_id(db, message.client_message_id)
            if existing:
                return existing
        raise


async def delete_message(db: AsyncSession, message_id: int) -> bool:
    db_message = await get_message_by_id(db, message_id)
    if not db_message:
        return False
    await db.delete(db_message)
    await db.commit()
    return True


async def delete_messages_by_room(db: AsyncSession, room_id: int) -> int:
    res = await db.execute(delete(Message).where(Message.room_id == room_id))
    return res.rowcount or 0


# room
async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    res = await db.execute(select(Room).filter(Room.id == room_id))
    return res.scalar_one_or_none()


async def get_room_by_name(db: AsyncSession, name: str) -> Optional[Room]:
    res = await db.execute(select(Room).filter(Room.name == name))
    return res.scalar_one_or_none()


async def create_room(db: AsyncSession, room: RoomCreate, owner_id: int | None = None) -> Room:
    db_room = Room(
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
    db.add(db_room)
    try:
        await db.commit()
        await db.refresh(db_room)
        return db_room
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_entry_error(e, "name"):
            raise ValueError(f"Room {room.name} already exists")
        else:
            raise


async def get_all_rooms(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Room]:
    res = await db.execute(
        select(Room).order_by(Room.created_at.desc()).offset(skip).limit(limit)
    )
    return res.scalars().all()


async def get_rooms_by_owner(db: AsyncSession, owner_id: int) -> List[Room]:
    res = await db.execute(
        select(Room)
        .where(Room.owner_id == owner_id)
        .order_by(Room.created_at.desc())
    )
    return res.scalars().all()


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
    for field in allowed_fields:
        if field in payload and payload[field] is not None:
            setattr(db_room, field, payload[field])

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
        db_room.peak_online_members = online_members
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
    await db.delete(db_room)
    await db.commit()
    return True


__all__ = [
    "AVATAR_KEYS",
    "create_message",
    "create_room",
    "create_user",
    "delete_message",
    "delete_room",
    "delete_user",
    "get_all_rooms",
    "get_message_by_id",
    "get_message_by_room",
    "get_messages_with_authors_by_room",
    "get_messages_page_by_room",
    "get_room_by_id",
    "get_room_by_name",
    "get_rooms_by_owner",
    "get_user_by_id",
    "get_user_by_username",
    "get_user_count",
    "serialize_message",
    "update_room",
    "update_room_peak_online_members",
    "update_user",
    "update_user_profile",
]
