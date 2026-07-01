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
from normal_system.repositories.friend import (
    create_private_message,
    get_friendship,
    list_private_messages,
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


def private_room_name(user_id: int, friend_id: int) -> str:
    low_user_id, high_user_id = (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)
    return f"private_{low_user_id}_{high_user_id}"


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
        print(f"User {user_id} connected (sid: {sid})")


@sio.event
async def disconnect(sid: str):
    changed_counts = room_presence.disconnect(sid)
    for room_id, online_members in changed_counts.items():
        await sio.emit(
            "room_member_count",
            {"room_id": room_id, "online_members": online_members},
            room=f"room_{room_id}",
        )
    print(f"Client {sid} disconnected")


@sio.event
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


@sio.event
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
                            content=f"-- {user.nickname or user.username} left the room --",
                            room_id=room_id,
                        ),
                        user_id=user_id,
                        message_type="system",
                    )
                    message_data = serialize_message(db_message, user).model_dump(mode="json")
                    await sio.emit("new_message", message_data, room=f"room_{room_id}")


@sio.event
async def join_private_chat(sid: str, data: dict):
    friend_id = data.get("friend_id")
    if not _is_strict_int(friend_id):
        await sio.emit("private_chat_error", {"message": "friend_id must be an integer"}, to=sid)
        return
    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("private_chat_error", {"message": "Authentication required"}, to=sid)
        return

    async with async_session() as db:
        friend = await get_user_by_id(db, friend_id)
        friendship = await get_friendship(db, user_id, friend_id)
        if not friend or not friendship:
            await sio.emit("private_chat_error", {"message": "Only friends can join private chat"}, to=sid)
            return
        page = await list_private_messages(db, user_id=user_id, friend_id=friend_id, limit=20)

    await sio.enter_room(sid, private_room_name(user_id, friend_id))
    await sio.emit("private_previous_messages", [item.model_dump(mode="json") for item in page.items], to=sid)


@sio.event
async def leave_private_chat(sid: str, data: dict):
    friend_id = data.get("friend_id")
    if not _is_strict_int(friend_id):
        return
    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        return
    await sio.leave_room(sid, private_room_name(user_id, friend_id))


@sio.event
async def send_private_message(sid: str, data: dict):
    recipient_id = data.get("recipient_id")
    content = data.get("content")
    client_message_id = data.get("client_message_id")

    if not _is_strict_int(recipient_id) or not isinstance(content, str) or not content.strip():
        await sio.emit("private_chat_error", {"message": "Invalid private message payload"}, to=sid)
        return
    if client_message_id is not None and (
        not isinstance(client_message_id, str) or len(client_message_id) > 64
    ):
        await sio.emit("private_chat_error", {"message": "client_message_id is invalid"}, to=sid)
        return

    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        await sio.emit("private_chat_error", {"message": "Authentication required"}, to=sid)
        return

    async with async_session() as db:
        recipient = await get_user_by_id(db, recipient_id)
        if not recipient:
            await sio.emit("private_chat_error", {"message": "Recipient not found"}, to=sid)
            return
        try:
            db_message = await create_private_message(
                db,
                sender_id=user_id,
                recipient_id=recipient_id,
                content=content.strip(),
                client_message_id=client_message_id,
            )
        except PermissionError:
            await sio.emit("private_chat_error", {"message": "Only friends can send private messages"}, to=sid)
            return
        sender = await get_user_by_id(db, db_message.sender_id)
        if not sender:
            await sio.emit("private_chat_error", {"message": "Sender not found"}, to=sid)
            return
        message_data = {
            "id": db_message.id,
            "sender_id": db_message.sender_id,
            "recipient_id": db_message.recipient_id,
            "content": db_message.content,
            "client_message_id": db_message.client_message_id,
            "author": {
                "id": sender.id,
                "username": sender.username,
                "nickname": sender.nickname,
                "bio": sender.bio,
                "avatar_key": sender.avatar_key,
                "created_at": sender.created_at.isoformat(),
            },
            "created_at": db_message.created_at.isoformat(),
        }

    await sio.emit("private_message_ack", message_data, to=sid)
    await sio.emit("private_new_message", message_data, room=private_room_name(user_id, recipient_id))
