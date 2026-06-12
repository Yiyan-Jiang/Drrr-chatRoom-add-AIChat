from normal_system.routers.user import router as user_router
from normal_system.routers.auth import router as auth_router
from normal_system.routers.room import router as room_router
from normal_system.routers.message import router as message_router
from normal_system.routers.socket import sio as socket_io_server
from normal_system.routers.gate import router as gate_router
from normal_system.routers.github import router as github_router

__all__ = [
    "user_router",
    "auth_router",
    "room_router",
    "message_router",
    "socket_io_server",
    "gate_router",
    "github_router",
]
