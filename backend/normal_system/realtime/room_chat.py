from common.normal_database import async_session
from normal_system.repositories.user import get_user_by_id
from normal_system.repositories.room import get_room_by_id
from normal_system.repositories.message import get_messages_with_authors_by_room, serialize_message
from normal_system.services.message import create_message
from normal_system.services.room import update_room_peak_online_members
from normal_system.schemas import MessageCreate
from normal_system.realtime.connection import _is_strict_int, get_current_user_id
from normal_system.realtime.publisher import emit_room_member_count, emit_room_members
from normal_system.realtime.server import room_presence, sio


async def join_room(sid: str, data: dict):
    room_id = data.get('room_id')
    if not _is_strict_int(room_id):
        await sio.emit("error", {"message": "room_id must be an integer"}, to=sid)
        return
    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("error", {"message": "Authentication required"}, to=sid)
        return

    async with async_session() as db:
        room = await get_room_by_id(db, room_id)
        if not room:
            await sio.emit("error", {"message": "Room not found"}, to=sid)
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
            print(f"Failed to update room peak online members: {exc}")
    await emit_room_member_count(room_id)
    await emit_room_members(room_id)

    async with async_session() as db:
        messages = await get_messages_with_authors_by_room(db, room_id)
        messages_data = [message.model_dump(mode="json") for message in messages]

    await sio.emit("previous_messages", messages_data, to=sid)
    print(f"User {user_id} joined room {room_id}")


async def send_message(sid: str, data: dict):
    room_id = data.get('room_id')
    content = data.get('content')
    client_message_id = data.get('client_message_id')

    if not _is_strict_int(room_id) or not isinstance(content, str) or not content.strip():
        await sio.emit("error", {"message": "Invalid message payload"}, to=sid)
        return
    if client_message_id is not None and (
        not isinstance(client_message_id, str) or len(client_message_id) > 64
    ):
        await sio.emit("error", {"message": "client_message_id is invalid"}, to=sid)
        return

    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("error", {"message": "Authentication required"}, to=sid)
        return

    message_create = MessageCreate(
        content=content.strip(),
        room_id=int(room_id),
        client_message_id=client_message_id,
    )

    async with async_session() as db:
        room = await get_room_by_id(db, int(room_id))
        if not room:
            await sio.emit("error", {"message": "Room not found"}, to=sid)
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
    print(f"User {user_id} sent message in room {room_id}")


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
                            content=f"-- {user.nickname or user.username} left the room --",
                            room_id=room_id,
                        ),
                        user_id=user_id,
                        message_type="system",
                    )
                    message_data = serialize_message(db_message, user).model_dump(mode="json")
                    await sio.emit("new_message", message_data, room=f"room_{room_id}")
