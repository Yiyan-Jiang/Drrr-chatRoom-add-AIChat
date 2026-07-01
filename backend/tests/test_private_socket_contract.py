from pathlib import Path
import py_compile
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def test_socket_router_defines_private_chat_events():
    socket_path = ROOT / "normal_system" / "routers" / "socket.py"
    content = socket_path.read_text(encoding="utf-8")

    assert "async def join_private_chat" in content
    assert "async def leave_private_chat" in content
    assert "async def send_private_message" in content
    assert "private_message_ack" in content
    assert "private_new_message" in content
    assert "private_chat_error" in content


def test_socket_router_is_valid_python():
    socket_path = ROOT / "normal_system" / "routers" / "socket.py"

    with tempfile.TemporaryDirectory() as temp_dir:
        py_compile.compile(str(socket_path), cfile=str(Path(temp_dir) / "socket.pyc"), doraise=True)


def test_private_chat_socket_uses_friend_repository_and_pair_room():
    socket_path = ROOT / "normal_system" / "routers" / "socket.py"
    content = socket_path.read_text(encoding="utf-8")

    assert "create_private_message" in content
    assert "get_friendship" in content
    assert "list_private_messages" in content
    assert "private_{low_user_id}_{high_user_id}" in content
    assert "Only friends can" in content
