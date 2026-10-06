from common.normal_database import async_session
from normal_system.repositories.user import get_user_by_id
from normal_system.repositories.friend import get_friendship
from normal_system.repositories.private_message import list_private_messages
from normal_system.services.private_message import create_private_message
from normal_system.realtime.connection import _is_strict_int, get_current_user_id
from normal_system.realtime.publisher import private_room_name
from normal_system.realtime.server import sio


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


async def leave_private_chat(sid: str, data: dict):
    friend_id = data.get("friend_id")
    if not _is_strict_int(friend_id):
        return
    try:
        user_id = await get_current_user_id(sid)
    except ValueError:
        return
    await sio.leave_room(sid, private_room_name(user_id, friend_id))


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
        except ValueError as exc:
            await sio.emit("private_chat_error", {"message": str(exc)}, to=sid)
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
