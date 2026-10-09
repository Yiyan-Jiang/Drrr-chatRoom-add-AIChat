import asyncio
from contextlib import ExitStack
import importlib
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault(
    "DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms"
)
os.environ.setdefault("CHAT_JWT_SECRET", "realtime-contract-test-secret-with-32-bytes")


EVENT_MODULES = {
    "connect": "connection",
    "disconnect": "connection",
    "join_room": "room_chat",
    "leave_room": "room_chat",
    "send_message": "room_chat",
    "join_private_chat": "private_chat",
    "leave_private_chat": "private_chat",
    "send_private_message": "private_chat",
}


def test_socket_registration_uses_one_server_and_exact_original_events():
    from normal_system.routers import socket

    assert Path(socket.__file__).parents[1].joinpath("realtime", "server.py").exists()
    from normal_system.realtime import server

    assert socket.sio is server.sio
    assert set(server.sio.handlers) == {"/"}
    assert set(server.sio.handlers["/"]) == set(EVENT_MODULES)
    for name, module_name in EVENT_MODULES.items():
        module = importlib.import_module(f"normal_system.realtime.{module_name}")
        assert server.sio.handlers["/"][name] is getattr(module, name)
        assert getattr(socket, name) is getattr(module, name)


def test_server_and_publisher_import_without_registering_socket_handlers():
    source = """
import sys
from normal_system.realtime import server, publisher
assert server.sio.handlers == {}
assert publisher.sio is server.sio
assert publisher.room_presence is server.room_presence
assert 'normal_system.routers.socket' not in sys.modules
from normal_system.routers import socket
assert socket.sio is server.sio
assert len(server.sio.handlers['/']) == 8
"""
    completed = subprocess.run(
        [sys.executable, "-c", source],
        cwd=Path(__file__).parents[1],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr


def run_realtime(scenario):
    assert (
        Path(__file__)
        .parents[1]
        .joinpath("normal_system", "realtime", "server.py")
        .exists()
    )
    from common.normal_database import Login
    from normal_system.models import Friendship, Room, User
    from normal_system.realtime import (
        connection,
        private_chat,
        publisher,
        room_chat,
        server,
    )
    from normal_system.services.room_presence import RoomPresence

    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        calls = []
        presence = RoomPresence()
        transport_sessions = {
            "alice": {"user_id": 1},
            "alice-tab": {"user_id": 1},
            "bob": {"user_id": 2},
        }
        try:
            async with engine.begin() as db:
                await db.run_sync(Login.metadata.create_all)
            async with sessions() as db:
                db.add_all(
                    [
                        User(
                            id=1,
                            username="alice",
                            password="unused",
                            nickname="Alice",
                            bio="alice-bio",
                            avatar_key="kanra",
                        ),
                        User(
                            id=2,
                            username="bob",
                            password="unused",
                            nickname="Bob",
                            bio="bob-bio",
                            avatar_key="izaya",
                        ),
                        Room(id=1, name="room1", owner_id=1),
                        Friendship(user_low_id=1, user_high_id=2),
                    ]
                )
                await db.commit()

            @event.listens_for(engine.sync_engine, "commit")
            def on_commit(_connection):
                calls.append(("commit",))

            async def emit(name, data, **kwargs):
                calls.append((name, data, kwargs))

            async def get_session(sid):
                return transport_sessions.get(sid, {})

            with ExitStack() as stack:
                for module in (connection, private_chat, publisher, room_chat):
                    if hasattr(module, "async_session"):
                        stack.enter_context(
                            patch.object(module, "async_session", sessions)
                        )
                    if hasattr(module, "room_presence"):
                        stack.enter_context(
                            patch.object(module, "room_presence", presence)
                        )
                stack.enter_context(patch.object(server, "room_presence", presence))
                stack.enter_context(
                    patch.object(server.sio, "emit", AsyncMock(side_effect=emit))
                )
                stack.enter_context(
                    patch.object(
                        server.sio, "get_session", AsyncMock(side_effect=get_session)
                    )
                )
                for method in (
                    "disconnect",
                    "save_session",
                    "enter_room",
                    "leave_room",
                ):
                    stack.enter_context(patch.object(server.sio, method, AsyncMock()))
                await scenario(
                    connection,
                    room_chat,
                    private_chat,
                    publisher,
                    server.sio,
                    presence,
                    sessions,
                    calls,
                )
        finally:
            await engine.dispose()

    asyncio.run(run())


@pytest.mark.parametrize(
    "auth", [None, {}, {"token": ""}, {"token": True}, {"token": "invalid"}]
)
def test_connect_rejects_invalid_auth_by_disconnecting_without_session(auth):
    async def scenario(
        connection, _room, _private, _publisher, sio, _presence, _sessions, calls
    ):
        result = await connection.connect("unknown", {}, auth)
        assert result is None
        sio.disconnect.assert_awaited_once_with("unknown")
        sio.save_session.assert_not_awaited()
        assert calls == []

    run_realtime(scenario)


@pytest.mark.parametrize("user_id,exists", [(1, True), (99, False)])
def test_connect_preserves_token_and_user_validation(user_id, exists):
    from common.auth import create_access_token

    async def scenario(
        connection, _room, _private, _publisher, sio, _presence, _sessions, calls
    ):
        token, _expires_in = create_access_token(user_id)
        assert (
            await connection.connect("unknown", {}, {"token": " " + token + " "})
            is None
        )
        if exists:
            sio.save_session.assert_awaited_once_with("unknown", {"user_id": user_id})
            sio.disconnect.assert_not_awaited()
        else:
            sio.disconnect.assert_awaited_once_with("unknown")
            sio.save_session.assert_not_awaited()
        assert calls == []

    run_realtime(scenario)


def test_group_message_commits_before_ack_and_broadcast_and_keeps_replay_error():
    from normal_system.models import Message

    async def scenario(
        _connection, room, _private, _publisher, _sio, _presence, sessions, calls
    ):
        payload = {"room_id": 1, "content": " hello ", "client_message_id": "group-1"}
        await room.send_message("alice", payload)
        assert [call[0] for call in calls] == ["commit", "message_ack", "new_message"]
        ack, broadcast = calls[1:]
        assert ack[1] == broadcast[1]
        assert ack[2] == {"to": "alice"}
        assert broadcast[2] == {"room": "room_1"}
        assert ack[1]["content"] == "hello"
        assert ack[1]["client_message_id"] == "group-1"
        assert ack[1]["author"]["username"] == "alice"
        async with sessions() as db:
            stored = (await db.execute(select(Message))).scalars().all()
            assert len(stored) == 1
            assert stored[0].id == ack[1]["id"]
        calls.clear()
        await room.send_message("alice", payload)
        assert [call[0] for call in calls] == ["message_ack", "new_message"]
        assert calls[0][1] == ack[1]
        calls.clear()
        await room.send_message("bob", payload)
        assert calls == [
            (
                "error",
                {"message": "client_message_id belongs to another conversation"},
                {"to": "bob"},
            )
        ]

    run_realtime(scenario)


def test_private_message_commits_before_ack_and_preserves_complete_author_payload():
    from normal_system.models import PrivateMessage, User

    async def scenario(
        _connection, _room, private, publisher, _sio, _presence, sessions, calls
    ):
        await private.send_private_message(
            "bob",
            {"recipient_id": 1, "content": " hello ", "client_message_id": "private-1"},
        )
        assert [call[0] for call in calls] == [
            "commit",
            "private_message_ack",
            "private_new_message",
        ]
        ack, broadcast = calls[1:]
        assert ack[1] == broadcast[1]
        assert ack[2] == {"to": "bob"}
        assert broadcast[2] == {"room": "private_1_2"}
        assert (
            publisher.private_room_name(2, 1)
            == publisher.private_room_name(1, 2)
            == "private_1_2"
        )
        async with sessions() as db:
            sender = await db.get(User, 2)
            message = (await db.execute(select(PrivateMessage))).scalar_one()
            assert ack[1] == {
                "id": message.id,
                "sender_id": 2,
                "recipient_id": 1,
                "content": "hello",
                "client_message_id": "private-1",
                "author": {
                    "id": 2,
                    "username": "bob",
                    "nickname": "Bob",
                    "bio": "bob-bio",
                    "avatar_key": "izaya",
                    "created_at": sender.created_at.isoformat(),
                },
                "created_at": message.created_at.isoformat(),
            }

    run_realtime(scenario)


def test_private_friend_permission_error_emits_no_ack_or_broadcast():
    from normal_system.models import Friendship, PrivateMessage

    async def scenario(
        _connection, _room, private, _publisher, sio, _presence, sessions, calls
    ):
        async with sessions() as db:
            friendship = (await db.execute(select(Friendship))).scalar_one()
            await db.delete(friendship)
            await db.commit()
        calls.clear()
        await private.join_private_chat("alice", {"friend_id": 2})
        assert calls == [
            (
                "private_chat_error",
                {"message": "Only friends can join private chat"},
                {"to": "alice"},
            )
        ]
        sio.enter_room.assert_not_awaited()
        calls.clear()
        await private.send_private_message(
            "alice", {"recipient_id": 2, "content": "hello"}
        )
        assert calls == [
            (
                "private_chat_error",
                {"message": "Only friends can send private messages"},
                {"to": "alice"},
            )
        ]
        async with sessions() as db:
            assert (await db.execute(select(PrivateMessage))).scalars().all() == []

    run_realtime(scenario)


def test_join_leave_keeps_order_unique_user_presence_and_system_message():
    from normal_system.models import Message

    async def scenario(
        connection, room, _private, _publisher, sio, presence, sessions, calls
    ):
        await room.join_room("alice", {"room_id": 1})
        assert [call[0] for call in calls] == [
            "user_joined",
            "commit",
            "new_message",
            "room_member_count",
            "room_members",
            "previous_messages",
        ]
        assert calls[0] == (
            "user_joined",
            {"user_id": 1, "room_id": 1},
            {"room": "room_1", "skip_sid": "alice"},
        )
        joined_message = calls[2][1]
        assert joined_message["content"] == "-- Alice joined the room --"
        assert joined_message["message_type"] == "system"
        assert joined_message["user_id"] == 1
        assert joined_message["author"]["nickname"] == "Alice"
        assert calls[2][2] == {"room": "room_1"}
        async with sessions() as db:
            stored = (await db.execute(select(Message))).scalar_one()
            assert stored.id == joined_message["id"]
            assert stored.content == joined_message["content"]
            assert stored.message_type == "system"
        assert calls[3][1] == {"room_id": 1, "online_members": 1}
        assert calls[4][1] == {
            "room_id": 1,
            "members": [
                {
                    "id": 1,
                    "username": "alice",
                    "nickname": "Alice",
                    "avatar_key": "kanra",
                }
            ],
        }
        assert calls[5] == ("previous_messages", [joined_message], {"to": "alice"})
        sio.enter_room.assert_awaited_once_with("alice", "room_1")
        calls.clear()
        await room.join_room("alice", {"room_id": 1})
        assert calls == []
        assert sio.enter_room.await_count == 1
        await room.join_room("alice-tab", {"room_id": 1})
        assert [call[0] for call in calls] == [
            "room_member_count",
            "room_members",
            "previous_messages",
        ]
        assert calls[-1][1] == [joined_message]
        assert presence.count(1) == 1
        calls.clear()
        await room.join_room("bob", {"room_id": 1})
        assert [call[0] for call in calls] == [
            "user_joined",
            "commit",
            "commit",
            "new_message",
            "room_member_count",
            "room_members",
            "previous_messages",
        ]
        assert calls[3][1]["content"] == "-- Bob joined the room --"
        assert calls[3][1]["message_type"] == "system"
        assert presence.count(1) == 2
        calls.clear()
        await room.leave_room("alice", {"room_id": 1})
        assert [call[0] for call in calls] == ["room_member_count", "room_members"]
        assert presence.members(1) == [1, 2]
        calls.clear()
        await room.leave_room("alice-tab", {"room_id": 1})
        assert [call[0] for call in calls] == [
            "room_member_count",
            "room_members",
            "commit",
            "new_message",
        ]
        assert calls[-1][1]["content"] == "-- Alice left the room --"
        assert calls[-1][1]["message_type"] == "system"
        assert calls[-1][2] == {"room": "room_1"}
        calls.clear()
        await room.leave_room("alice-tab", {"room_id": 1})
        assert calls == []
        await connection.disconnect("bob")
        assert calls == [
            (
                "room_member_count",
                {"room_id": 1, "online_members": 0},
                {"room": "room_1"},
            )
        ]
        async with sessions() as db:
            assert len((await db.execute(select(Message))).scalars().all()) == 3

    run_realtime(scenario)


def test_private_join_history_and_leave_keep_symmetric_room():
    async def scenario(
        _connection, _room, private, _publisher, sio, _presence, _sessions, calls
    ):
        await private.send_private_message(
            "bob", {"recipient_id": 1, "content": "hello"}
        )
        message = calls[-1][1]
        calls.clear()
        await private.join_private_chat("alice", {"friend_id": 2})
        sio.enter_room.assert_awaited_once_with("alice", "private_1_2")
        assert calls == [("private_previous_messages", [message], {"to": "alice"})]
        await private.leave_private_chat("alice", {"friend_id": 2})
        sio.leave_room.assert_awaited_once_with("alice", "private_1_2")

    run_realtime(scenario)


@pytest.mark.parametrize(
    "module_name,method,payload,event_name,error",
    [
        ("room", "join_room", {"room_id": True}, "error", "room_id must be an integer"),
        (
            "room",
            "send_message",
            {"room_id": True, "content": "hello"},
            "error",
            "Invalid message payload",
        ),
        (
            "room",
            "send_message",
            {"room_id": 1, "content": " "},
            "error",
            "Invalid message payload",
        ),
        (
            "room",
            "send_message",
            {"room_id": 1, "content": "hello", "client_message_id": 1},
            "error",
            "client_message_id is invalid",
        ),
        (
            "private",
            "join_private_chat",
            {"friend_id": True},
            "private_chat_error",
            "friend_id must be an integer",
        ),
        (
            "private",
            "send_private_message",
            {"recipient_id": True, "content": "hello"},
            "private_chat_error",
            "Invalid private message payload",
        ),
        (
            "private",
            "send_private_message",
            {"recipient_id": 2, "content": "hello", "client_message_id": "x" * 65},
            "private_chat_error",
            "client_message_id is invalid",
        ),
    ],
)
def test_invalid_payloads_keep_original_error_and_do_not_write(
    module_name, method, payload, event_name, error
):
    async def scenario(
        _connection, room, private, _publisher, sio, _presence, _sessions, calls
    ):
        handler = getattr(room if module_name == "room" else private, method)
        await handler("alice", payload)
        assert calls == [(event_name, {"message": error}, {"to": "alice"})]
        sio.get_session.assert_not_awaited()

    run_realtime(scenario)


def test_room_delete_commits_clears_presence_then_publishes_same_event():
    from normal_system.models import Room

    async def scenario(
        _connection, _room, _private, publisher, _sio, presence, sessions, calls
    ):
        from normal_system.routers import room

        presence.join("alice", 1, user_id=1)
        with patch.object(room, "room_presence", presence):
            async with sessions() as db:
                await room.delete_existing_room(1, db, user_id=1)
        assert presence.count(1) == 0
        assert calls == [
            ("commit",),
            ("room_deleted", {"room_id": 1}, {"room": "room_1"}),
        ]
        async with sessions() as db:
            assert await db.get(Room, 1) is None

    run_realtime(scenario)
