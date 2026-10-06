import ast
import asyncio
import importlib
import os
from pathlib import Path
from types import TracebackType
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")


@pytest.mark.parametrize(
    "module_name,function_names",
    [
        ("user", ("add_user", "get_user_by_id", "remove_user_and_owned_rooms", "set_user_profile")),
        ("room", ("add_room", "get_room_by_id", "remove_room", "set_room_fields")),
        ("message", ("add_message", "get_messages_page_by_room", "serialize_message")),
        ("private_message", ("add_private_message", "list_private_messages")),
    ],
)
def test_repository_operations_are_defined_in_concrete_modules(module_name, function_names):
    module = importlib.import_module(f"normal_system.repositories.{module_name}")
    for name in function_names:
        assert getattr(module, name).__module__ == module.__name__


def test_repository_package_only_declares_explicit_exports():
    source = Path(__file__).parents[1] / "normal_system" / "repositories" / "__init__.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    assert all(isinstance(node, (ast.ImportFrom, ast.Assign)) for node in tree.body)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            assert all(alias.name != "*" for alias in node.names)
        else:
            assert [target.id for target in node.targets] == ["__all__"]


def test_query_exports_are_concrete_and_friend_has_no_private_message_exports():
    from normal_system import repositories
    from normal_system.repositories import friend, message, private_message, room, user

    for module in (message, room, user):
        for name in repositories.__all__:
            if hasattr(module, name):
                assert getattr(repositories, name) is getattr(module, name)
    for name in ("create_private_message", "list_private_messages", "get_private_message_by_client_message_id"):
        assert not hasattr(friend, name)
    assert private_message.list_private_messages.__module__ == private_message.__name__


@pytest.mark.parametrize("router_name", ["auth", "user", "room", "message", "post", "friend"])
def test_http_routers_use_the_shared_database_dependency(router_name):
    from common.normal_database import get_db

    module = importlib.import_module(f"normal_system.routers.{router_name}")
    assert module.get_db is get_db
    source = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(node, ast.AsyncFunctionDef) and node.name == "get_db" for node in source.body)
    assert not hasattr(module, "async_session")
    routers = [module.router]
    if router_name == "friend":
        routers.append(module.private_message_router)
    for router in routers:
        for route in router.routes:
            if router_name == "room" and route.path == "/rooms/viewers/count":
                assert route.dependant.dependencies == []
                continue
            assert any(dependency.call is get_db for dependency in route.dependant.dependencies)


@pytest.mark.parametrize("raise_in_request", [False, True])
def test_shared_database_dependency_closes_session_without_committing(raise_in_request):
    from common.normal_database import get_db

    async def scenario():
        session = AsyncMock()
        manager = MagicMock()
        manager.__aenter__ = AsyncMock(return_value=session)
        manager.__aexit__ = AsyncMock(return_value=False)
        factory = MagicMock(return_value=manager)
        with patch("common.normal_database.async_session", factory):
            dependency = get_db()
            assert await anext(dependency) is session
            if raise_in_request:
                error = ValueError("request failed")
                with pytest.raises(ValueError, match="request failed"):
                    await dependency.athrow(error)
                manager.__aexit__.assert_awaited_once_with(ValueError, error, ANY)
                assert isinstance(manager.__aexit__.await_args.args[2], TracebackType)
            else:
                with pytest.raises(StopAsyncIteration):
                    await anext(dependency)
                manager.__aexit__.assert_awaited_once_with(None, None, None)
        factory.assert_called_once_with()
        session.commit.assert_not_awaited()
        session.rollback.assert_not_awaited()

    asyncio.run(scenario())
