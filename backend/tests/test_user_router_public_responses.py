from datetime import datetime
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/chat_rooms")

from common.dependencies import get_current_user_id, require_gate_passed
from normal_system.routers import user as user_router


def test_register_response_does_not_include_password():
    app = build_user_app()
    db = object()
    app.dependency_overrides[user_router.get_db] = lambda: db
    app.dependency_overrides[require_gate_passed] = lambda: None

    with patch(
        "normal_system.routers.user.create_user",
        AsyncMock(return_value=build_user(password="hashed-secret")),
    ):
        response = TestClient(app).post(
            "/users/register",
            json={"username": "alice", "password": "plain-secret"},
        )

    assert response.status_code == 201
    assert "password" not in response.json()


def test_read_user_by_username_response_does_not_include_password():
    app = build_user_app()
    db = object()
    app.dependency_overrides[user_router.get_db] = lambda: db

    with patch(
        "normal_system.routers.user.get_user_by_username",
        AsyncMock(return_value=build_user(password="hashed-secret")),
    ):
        response = TestClient(app).get("/users/username/alice")

    assert response.status_code == 200
    assert "password" not in response.json()


def test_read_user_by_id_response_does_not_include_password():
    app = build_user_app()
    db = object()
    app.dependency_overrides[user_router.get_db] = lambda: db

    with patch(
        "normal_system.routers.user.get_user_by_id",
        AsyncMock(return_value=build_user(password="hashed-secret")),
    ):
        response = TestClient(app).get("/users/1")

    assert response.status_code == 200
    assert "password" not in response.json()


def test_update_user_response_does_not_include_password():
    app = build_user_app()
    db = object()
    app.dependency_overrides[user_router.get_db] = lambda: db
    app.dependency_overrides[get_current_user_id] = lambda: 1

    with patch(
        "normal_system.routers.user.update_user",
        AsyncMock(return_value=build_user(password="hashed-secret")),
    ):
        response = TestClient(app).put(
            "/users/1",
            json={"nickname": "Alice", "bio": "", "avatar_key": "kanra"},
        )

    assert response.status_code == 200
    assert "password" not in response.json()


def build_user_app() -> FastAPI:
    app = FastAPI()
    app.include_router(user_router.router)
    return app


def build_user(*, password: str):
    return SimpleNamespace(
        id=1,
        username="alice",
        password=password,
        nickname="Alice",
        bio="",
        avatar_key="kanra",
        created_at=datetime(2026, 1, 1),
    )
