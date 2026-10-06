from common.normal_database import async_session
from normal_system.repositories.user import get_user_by_id
from normal_system.realtime.server import room_presence, sio


async def emit_room_member_count(room_id: int):
    await sio.emit(
        "room_member_count",
        {"room_id": room_id, "online_members": room_presence.count(room_id)},
        room=f"room_{room_id}",
    )


async def emit_room_members(room_id: int):
    user_ids = room_presence.members(room_id)
    async with async_session() as db:
        users = []
        for user_id in user_ids:
            user = await get_user_by_id(db, user_id)
            if user:
                users.append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "nickname": user.nickname,
                        "avatar_key": user.avatar_key,
                    }
                )
    await sio.emit("room_members", {"room_id": room_id, "members": users}, room=f"room_{room_id}")


def private_room_name(user_id: int, friend_id: int) -> str:
    low_user_id, high_user_id = (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)
    return f"private_{low_user_id}_{high_user_id}"


async def emit_room_deleted(room_id: int):
    await sio.emit("room_deleted", {"room_id": room_id}, room=f"room_{room_id}")
