from socketio import AsyncServer

from common.auth import decode_access_token
from common.normal_database import async_session
from normal_system.repositories import (
    get_user_by_id,
    get_room_by_id,
    create_message,
    get_messages_with_authors_by_room,
    serialize_message,
    update_room_peak_online_members,
)
from normal_system.services.room_presence import RoomPresence
from normal_system.schemas import MessageCreate


def _is_strict_int(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


sio: AsyncServer = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_interval=25,
    ping_timeout=20,
)
room_presence = RoomPresence()


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


async def get_current_user_id(sid: str) -> int:
    session: dict = await sio.get_session(sid)
    user_id = session.get('user_id')
    if user_id is None:
        raise ValueError("User not found")
    return user_id


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None):
    if not isinstance(auth, dict) or not auth:
        await sio.disconnect(sid)
        return

    token = auth.get("token")
    if isinstance(token, str) and token.strip():
        user_id = decode_access_token(token.strip())
    else:
        user_id = None

    if user_id is None:
        await sio.disconnect(sid)
        return

    async with async_session() as db:
        user = await get_user_by_id(db, user_id)
        if not user:
            await sio.disconnect(sid)
            return

        await sio.save_session(sid, {"user_id": user_id})
        print(f"用户 {user_id} 已连接 (sid: {sid})")


@sio.event
async def disconnect(sid: str):
    changed_counts = room_presence.disconnect(sid)
    for room_id, online_members in changed_counts.items():
        await sio.emit(
            "room_member_count",
            {"room_id": room_id, "online_members": online_members},
            room=f"room_{room_id}",
        )
    print(f"客户端 {sid} 已断开")


@sio.event
async def join_room(sid: str, data: dict):
    room_id = data.get('room_id')
    if not _is_strict_int(room_id):
        await sio.emit("error", {"message": "room_id 必须是整数"}, to=sid)
        return
    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("error", {"message": "请先登录"}, to=sid)
        return

    async with async_session() as db:
        room = await get_room_by_id(db, room_id)
        if not room:
            await sio.emit("error", {"message": "聊天室不存在"}, to=sid)
            return

    room_name = f"room_{room_id}"
    if room_presence.is_sid_in_room(sid, room_id):
        return

    await sio.enter_room(sid, room_name)
    user_entered = room_presence.join_user_entered_room(sid, room_id, user_id=user_id)

    if user_entered:
        await sio.emit(
            "user_joined",
            {"user_id": user_id, "room_id": room_id},
            room=room_name,
            skip_sid=sid,
        )
        try:
            async with async_session() as db:
                await update_room_peak_online_members(
                    db,
                    room_id,
                    len(room_presence.members(room_id)),
                )
        except Exception as exc:
            print(f"更新房间峰值在线人数失败: {exc}")
    await emit_room_member_count(room_id)
    await emit_room_members(room_id)

    async with async_session() as db:
        messages = await get_messages_with_authors_by_room(db, room_id)
        messages_data = [message.model_dump(mode="json") for message in messages]

    await sio.emit("previous_messages", messages_data, to=sid)
    print(f" 用户 {user_id} 加入房间 {room_id}")


@sio.event
async def send_message(sid: str, data: dict):
    room_id = data.get('room_id')
    content = data.get('content')
    client_message_id = data.get('client_message_id')

    if not _is_strict_int(room_id) or not isinstance(content, str) or not content.strip():
        await sio.emit("error", {"message": "参数错误"}, to=sid)
        return
    if client_message_id is not None and (
        not isinstance(client_message_id, str) or len(client_message_id) > 64
    ):
        await sio.emit("error", {"message": "client_message_id 无效"}, to=sid)
        return

    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("error", {"message": "请先登录"}, to=sid)
        return

    message_create = MessageCreate(
        content=content.strip(),
        room_id=int(room_id),
        client_message_id=client_message_id,
    )

    async with async_session() as db:
        room = await get_room_by_id(db, int(room_id))
        if not room:
            await sio.emit("error", {"message": "聊天室不存在"}, to=sid)
            return
        try:
            db_message = await create_message(db, message_create, user_id)
        except ValueError as e:
            await sio.emit("error", {"message": str(e)}, to=sid)
            return
        user = await get_user_by_id(db, db_message.user_id) if db_message.user_id else None

    room_name = f"room_{room_id}"
    message_data = serialize_message(db_message, user).model_dump(mode="json")

    await sio.emit("message_ack", message_data, to=sid)
    await sio.emit("new_message", message_data, room=room_name)
    print(f" 用户 {user_id} 在房间 {room_id} 发送消息")


@sio.event
async def leave_room(sid: str, data: dict):
    room_id = data.get('room_id')
    if _is_strict_int(room_id):
        room_id = int(room_id)
        if not room_presence.is_sid_in_room(sid, room_id):
            return
        try:
            user_id = await get_current_user_id(sid)
        except ValueError:
            user_id = None
        user_left = room_presence.leave_user_left_room(sid, room_id)
        await sio.leave_room(sid, f"room_{room_id}")
        await emit_room_member_count(room_id)
        await emit_room_members(room_id)
        if user_left and user_id is not None:
            async with async_session() as db:
                user = await get_user_by_id(db, user_id)
                room = await get_room_by_id(db, room_id)
                if user and room:
                    db_message = await create_message(
                        db,
                        MessageCreate(
                            content=f"-- {user.nickname or user.username} 离开了房间 --",
                            room_id=room_id,
                        ),
                        user_id=user_id,
                        message_type="system",
                    )
                    message_data = serialize_message(db_message, user).model_dump(mode="json")
                    await sio.emit("new_message", message_data, room=f"room_{room_id}")
