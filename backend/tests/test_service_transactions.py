import ast
import asyncio
import importlib
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")


@pytest.mark.parametrize("module_name", ["user", "room", "message", "private_message", "friend", "post"])
def test_repositories_do_not_own_transactions_or_transport(module_name):
    source = Path(__file__).parents[1] / "normal_system" / "repositories" / f"{module_name}.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"commit", "rollback"}, module_name
        if isinstance(node, ast.ImportFrom):
            assert not any(part in (node.module or "") for part in ("fastapi", "starlette", "routers", "services", "common.passwords"))


def test_service_modules_do_not_import_transport_or_execute_sql():
    root = Path(__file__).parents[1] / "normal_system" / "services"
    for module_name in ("auth", "user", "room", "message", "private_message", "friend", "post"):
        tree = ast.parse((root / f"{module_name}.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "fastapi" not in (node.module or "")
                assert ".routers" not in (node.module or "")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"execute", "scalar", "get"}, module_name


def test_group_replay_returns_original_without_staging_or_commit():
    service = importlib.import_module("normal_system.services.message")
    from normal_system.schemas import MessageCreate

    async def scenario():
        db = AsyncMock()
        original = SimpleNamespace(user_id=1, room_id=2, content="original")
        with patch.object(service, "get_room_by_id", AsyncMock(return_value=object())), patch.object(
            service, "get_message_by_client_message_id", AsyncMock(return_value=original)
        ), patch.object(service, "add_message", Mock()) as add:
            replay = await service.create_message(db, MessageCreate(room_id=2, content="retry", client_message_id="key"), 1)
        assert replay is original
        add.assert_not_called()
        db.commit.assert_not_awaited()
        db.rollback.assert_not_awaited()
        db.refresh.assert_not_awaited()

    asyncio.run(scenario())


@pytest.mark.parametrize("private", [False, True])
def test_message_validation_precedes_replay_lookup(private):
    service = importlib.import_module(f"normal_system.services.{'private_message' if private else 'message'}")
    lookup = "get_friendship" if private else "get_room_by_id"
    replay = "get_private_message_by_client_message_id" if private else "get_message_by_client_message_id"

    async def scenario():
        db = AsyncMock()
        with patch.object(service, lookup, AsyncMock(return_value=None)), patch.object(service, replay, AsyncMock()) as find:
            if private:
                with pytest.raises(PermissionError, match="Only friends"):
                    await service.create_private_message(db, 1, 2, "retry", "key")
            else:
                from normal_system.schemas import MessageCreate

                with pytest.raises(ValueError, match="Room 2 does not exist"):
                    await service.create_message(db, MessageCreate(room_id=2, content="retry", client_message_id="key"), 1)
        find.assert_not_awaited()
        db.commit.assert_not_awaited()
        db.rollback.assert_not_awaited()

    asyncio.run(scenario())


@pytest.mark.parametrize("private", [False, True])
def test_message_refresh_conflict_rolls_back_before_scope_lookup(private):
    service = importlib.import_module(f"normal_system.services.{'private_message' if private else 'message'}")
    lookup = "get_friendship" if private else "get_room_by_id"
    replay = "get_private_message_by_client_message_id" if private else "get_message_by_client_message_id"

    async def scenario():
        db = AsyncMock()
        db.add = Mock()
        events = []
        original = SimpleNamespace(sender_id=1, recipient_id=2, user_id=1, room_id=2)
        calls = 0

        async def find(*args):
            nonlocal calls
            calls += 1
            events.append("lookup")
            return original if calls == 2 else None

        async def refresh(*args):
            events.append("refresh")
            raise IntegrityError("refresh", {}, Exception("duplicate"))

        db.commit.side_effect = lambda: events.append("commit")
        db.rollback.side_effect = lambda: events.append("rollback")
        db.refresh.side_effect = refresh
        with patch.object(service, lookup, AsyncMock(return_value=object())), patch.object(service, replay, find):
            if private:
                result = await service.create_private_message(db, 1, 2, "retry", "key")
            else:
                from normal_system.schemas import MessageCreate

                result = await service.create_message(db, MessageCreate(room_id=2, content="retry", client_message_id="key"), 1)
        assert result is original
        assert events == ["lookup", "commit", "refresh", "rollback", "lookup"]
        db.commit.assert_awaited_once()
        db.rollback.assert_awaited_once()

    asyncio.run(scenario())


@pytest.mark.parametrize("module_name", ["user", "room"])
@pytest.mark.parametrize("failure_at", ["commit", "refresh"])
@pytest.mark.parametrize("duplicate", [False, True])
def test_create_services_preserve_integrity_error_scope(module_name, failure_at, duplicate):
    service = importlib.import_module(f"normal_system.services.{module_name}")
    from normal_system.schemas import RoomCreate, UserCreate

    async def scenario():
        db = AsyncMock()
        db.add = Mock()
        error = IntegrityError("write", {}, Exception("duplicate"))
        getattr(db, failure_at).side_effect = error
        with patch.object(service, "is_duplicate_entry_error", return_value=duplicate) as classify:
            if module_name == "user":
                with patch.object(service, "run_in_threadpool", AsyncMock(return_value="hashed")):
                    with pytest.raises(ValueError if duplicate else IntegrityError) as raised:
                        await service.create_user(db, UserCreate(username="alice", password="password"))
            else:
                with pytest.raises(ValueError if duplicate else IntegrityError) as raised:
                    await service.create_room(db, RoomCreate(name="room"), owner_id=1)
        if duplicate:
            assert str(raised.value) == ("User alice already exists" if module_name == "user" else "Room room already exists")
        else:
            assert raised.value is error
        classify.assert_called_once_with(error, "username" if module_name == "user" else "name")
        db.commit.assert_awaited_once()
        db.rollback.assert_awaited_once()
        assert db.refresh.await_count == int(failure_at == "refresh")

    asyncio.run(scenario())


def test_room_update_with_no_changed_fields_still_commits_without_refresh():
    service = importlib.import_module("normal_system.services.room")
    from normal_system.schemas import RoomUpdate

    async def scenario():
        db = AsyncMock()
        room = SimpleNamespace(owner_id=1, name="room", description="d", notice="n", rules="r")
        with patch.object(service, "get_room_by_id", AsyncMock(return_value=room)):
            result = await service.update_room(db, 2, RoomUpdate(name=None), 1)
        assert result == {"name": "room", "description": "d", "notice": "n", "rules": "r"}
        db.commit.assert_awaited_once()
        db.refresh.assert_not_awaited()

    asyncio.run(scenario())


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_user_service_rejects_other_actor_before_query(operation):
    service = importlib.import_module("normal_system.services.user")
    from normal_system.schemas import UserUpdate

    async def scenario():
        db = AsyncMock()
        with patch.object(service, "get_user_by_id", AsyncMock()) as lookup:
            with pytest.raises(PermissionError, match=f"Cannot {operation} another user"):
                if operation == "update":
                    await service.update_user(db, 2, UserUpdate(nickname="nick", bio=""), requester_id=1)
                else:
                    await service.delete_user(db, 2, requester_id=1)
        lookup.assert_not_awaited()
        db.commit.assert_not_awaited()

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "module_name,operation,lookup,args",
    [
        ("user", "delete_user", "get_user_by_id", (1,)),
        ("room", "delete_room", "get_room_by_id", (1,)),
        ("message", "delete_message", "get_message_by_id", (1,)),
        ("friend", "delete_friendship", "get_friendship", (1, 2)),
        ("post", "delete_post", "get_post_by_id", (1, 2)),
        ("post", "delete_post_comment", "get_post_comment_by_id", (1, 2, 3)),
    ],
)
def test_missing_delete_does_not_commit(module_name, operation, lookup, args):
    service = importlib.import_module(f"normal_system.services.{module_name}")

    async def scenario():
        db = AsyncMock()
        with patch.object(service, lookup, AsyncMock(return_value=None)):
            assert await getattr(service, operation)(db, *args) is False
        db.commit.assert_not_awaited()
        db.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_comment_from_other_post_is_not_deleted_or_checked_as_its_author():
    service = importlib.import_module("normal_system.services.post")

    async def scenario():
        db = AsyncMock()
        with patch.object(service, "get_post_comment_by_id", AsyncMock(return_value=SimpleNamespace(post_id=9, author_id=4))):
            assert await service.delete_post_comment(db, 1, 2, 3) is False
        db.commit.assert_not_awaited()
        db.delete.assert_not_awaited()

    asyncio.run(scenario())


def test_legacy_authentication_hashes_in_threadpool_and_commits_before_token():
    service = importlib.import_module("normal_system.services.auth")
    from datetime import datetime
    from normal_system.schemas import LoginRequest

    async def scenario():
        db = AsyncMock()
        user = SimpleNamespace(
            id=1, username="alice", nickname="alice", bio="", avatar_key="kanra",
            password="legacy", created_at=datetime(2026, 1, 1),
        )
        events = []

        async def threadpool(function, *args):
            if function is service.verify_password:
                events.append("verify")
                assert args == ("password", "legacy")
                return True
            assert function is service.hash_password
            assert args == ("password",)
            events.append("hash")
            return "salted"

        async def commit():
            assert user.password == "salted"
            events.append("commit")

        def token(user_id):
            assert user_id == 1
            events.append("token")
            return "token", 3600

        db.commit.side_effect = commit
        with patch.object(service, "get_user_by_username", AsyncMock(return_value=user)), patch.object(
            service, "needs_password_upgrade", return_value=True
        ), patch.object(service, "run_in_threadpool", threadpool), patch.object(service, "create_access_token", token):
            response = await service.login_user(db, LoginRequest(username="alice", password="password"))
        assert response.access_token == "token"
        assert events == ["verify", "hash", "commit", "token"]
        db.refresh.assert_not_awaited()
        db.rollback.assert_not_awaited()

    asyncio.run(scenario())


def test_failed_legacy_upgrade_commit_propagates_without_issuing_token_or_added_rollback():
    service = importlib.import_module("normal_system.services.auth")
    from normal_system.schemas import LoginRequest

    async def scenario():
        db = AsyncMock()
        user = SimpleNamespace(id=1, password="legacy")
        error = IntegrityError("commit", {}, Exception("database failure"))
        db.commit.side_effect = error
        with patch.object(service, "get_user_by_username", AsyncMock(return_value=user)), patch.object(
            service, "needs_password_upgrade", return_value=True
        ), patch.object(service, "run_in_threadpool", AsyncMock(side_effect=[True, "salted"])), patch.object(
            service, "create_access_token", Mock()
        ) as token:
            with pytest.raises(IntegrityError) as raised:
                await service.login_user(db, LoginRequest(username="alice", password="password"))
        assert raised.value is error
        token.assert_not_called()
        db.rollback.assert_not_awaited()

    asyncio.run(scenario())


@pytest.mark.parametrize("online_members,commit_count", [(1, 0), (2, 1)])
def test_peak_service_only_commits_an_increase_and_refreshes_after_commit(online_members, commit_count):
    service = importlib.import_module("normal_system.services.room")

    async def scenario():
        db = AsyncMock()
        room = SimpleNamespace(peak_online_members=None)
        events = []
        db.commit.side_effect = lambda: events.append("commit")
        db.refresh.side_effect = lambda item: events.append("refresh")
        with patch.object(service, "get_room_by_id", AsyncMock(return_value=room)):
            assert await service.update_room_peak_online_members(db, 1, online_members) is room
        assert db.commit.await_count == commit_count
        assert db.refresh.await_count == commit_count
        assert events == ["commit", "refresh"] * commit_count

    asyncio.run(scenario())


@pytest.mark.parametrize("exists,conflict", [(True, False), (False, False), (False, True)])
def test_post_reaction_service_preserves_noop_and_conflict_transactions(exists, conflict):
    service = importlib.import_module("normal_system.services.post")

    async def scenario():
        db = AsyncMock()
        db.add = Mock()
        if conflict:
            db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
        with patch.object(service, "get_post_reaction_id", AsyncMock(return_value=9 if exists else None)):
            await service.like_post(db, 1, 2)
        assert db.commit.await_count == (0 if exists else 1)
        assert db.rollback.await_count == int(conflict)
        assert db.add.call_count == (0 if exists else 1)

    asyncio.run(scenario())


@pytest.mark.parametrize("state,actor,error", [("pending", 3, PermissionError), ("accepted", 2, ValueError)])
def test_friend_service_checks_recipient_and_state_before_writing(state, actor, error):
    service = importlib.import_module("normal_system.services.friend")

    async def scenario():
        db = AsyncMock()
        db.add = Mock()
        request = SimpleNamespace(requester_id=1, recipient_id=2, status=state)
        with patch.object(service, "get_friend_request_by_id", AsyncMock(return_value=request)):
            with pytest.raises(error):
                await service.accept_friend_request(db, 1, actor)
        db.add.assert_not_called()
        db.commit.assert_not_awaited()
        db.refresh.assert_not_awaited()

    asyncio.run(scenario())
