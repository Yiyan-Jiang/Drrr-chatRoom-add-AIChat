from socketio import AsyncServer

from normal_system.services.room_presence import RoomPresence

sio: AsyncServer = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_interval=25,
    ping_timeout=20,
)
room_presence = RoomPresence()
