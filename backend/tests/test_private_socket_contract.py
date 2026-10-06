from pathlib import Path
import py_compile
import tempfile
import os

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")


ROOT = Path(__file__).resolve().parents[1]


def test_socket_router_defines_private_chat_events():
    from normal_system.routers import socket
    from normal_system.realtime import private_chat

    for name in ("join_private_chat", "leave_private_chat", "send_private_message"):
        assert socket.sio.handlers["/"][name] is getattr(private_chat, name)
        assert getattr(private_chat, name).__module__ == private_chat.__name__


def test_socket_router_is_valid_python():
    with tempfile.TemporaryDirectory() as temp_dir:
        for path in [ROOT / "normal_system" / "routers" / "socket.py", *(ROOT / "normal_system" / "realtime").glob("*.py")]:
            py_compile.compile(str(path), cfile=str(Path(temp_dir) / (path.stem + ".pyc")), doraise=True)


def test_private_chat_socket_uses_friend_repository_and_pair_room():
    from normal_system.realtime import private_chat
    from normal_system.repositories.friend import get_friendship
    from normal_system.repositories.private_message import list_private_messages
    from normal_system.services.private_message import create_private_message

    assert private_chat.get_friendship is get_friendship
    assert private_chat.list_private_messages is list_private_messages
    assert private_chat.create_private_message is create_private_message
    assert private_chat.private_room_name(1, 2) == private_chat.private_room_name(2, 1) == "private_1_2"
