"""广播房间成员、人数和删除通知，并生成私聊频道名称。"""

from common.normal_database import async_session
from normal_system.repositories.user import get_user_by_id
from normal_system.realtime.server import room_presence, sio


async def emit_room_member_count(room_id: int):
    """向房间频道广播当前进程内的在线人数。"""
    await sio.emit(
        "room_member_count",
        {"room_id": room_id, "online_members": room_presence.count(room_id)},
        room=f"room_{room_id}",
    )


async def emit_room_members(room_id: int):
    """读取在线用户公开资料并向房间频道广播成员列表。"""
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
    await sio.emit(
        "room_members", {"room_id": room_id, "members": users}, room=f"room_{room_id}"
    )


def private_room_name(user_id: int, friend_id: int) -> str:
    """按排序后的用户 ID 生成双方共用的私聊频道名。"""
    low_user_id, high_user_id = (
        (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)
    )
    return f"private_{low_user_id}_{high_user_id}"


async def emit_room_deleted(room_id: int):
    """向房间频道广播房间已删除事件。"""
    await sio.emit("room_deleted", {"room_id": room_id}, room=f"room_{room_id}")
