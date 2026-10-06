from common.auth import decode_access_token
from common.normal_database import async_session
from normal_system.repositories.user import get_user_by_id
from normal_system.realtime.server import room_presence, sio


def _is_strict_int(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


async def get_current_user_id(sid: str) -> int:
    session: dict = await sio.get_session(sid)
    user_id = session.get('user_id')
    if user_id is None:
        raise ValueError("User not found")
    return user_id


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


async def disconnect(sid: str):
    changed_counts = room_presence.disconnect(sid)
    for room_id, online_members in changed_counts.items():
        await sio.emit(
            "room_member_count",
            {"room_id": room_id, "online_members": online_members},
            room=f"room_{room_id}",
        )
    print(f"Client {sid} disconnected")
