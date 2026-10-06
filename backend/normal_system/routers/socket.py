"""Register the application's Socket.IO events once on the shared server."""

from normal_system.realtime.connection import connect, disconnect
from normal_system.realtime.room_chat import join_room, leave_room, send_message
from normal_system.realtime.private_chat import join_private_chat, leave_private_chat, send_private_message
from normal_system.realtime.server import sio

sio.on("connect", handler=connect)
sio.on("disconnect", handler=disconnect)
sio.on("join_room", handler=join_room)
sio.on("send_message", handler=send_message)
sio.on("leave_room", handler=leave_room)
sio.on("join_private_chat", handler=join_private_chat)
sio.on("leave_private_chat", handler=leave_private_chat)
sio.on("send_private_message", handler=send_private_message)
