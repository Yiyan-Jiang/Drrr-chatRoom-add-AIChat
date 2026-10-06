import hashlib
import os
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/chat_rooms")

from common.dependencies import require_gate_passed
from normal_system.services.user import create_user
from normal_system.services import auth as auth_service
from normal_system.routers import auth as auth_router
from normal_system.schemas import UserCreate


def test_registration_uses_distinct_salted_password_hashes_that_fit_existing_column():
    import asyncio

    async def scenario():
        db = AsyncMock()
        db.add = Mock()
        first = await create_user(db, UserCreate(username="alice", password="same-password"))
        second = await create_user(db, UserCreate(username="bob", password="same-password"))
        assert first.password != second.password
        assert first.password.startswith("pbkdf2_sha256$")
        assert len(first.password) <= 128
        algorithm, iterations, salt, digest = first.password.split("$")
        assert int(iterations) >= 600_000
        assert len(bytes.fromhex(salt)) >= 16
        assert hashlib.pbkdf2_hmac("sha256", b"same-password", bytes.fromhex(salt), int(iterations)).hex() == digest

    asyncio.run(scenario())


def login_with_hash(stored_hash, password):
    db = AsyncMock()
    user = SimpleNamespace(
        id=1, username="alice", nickname="Alice", bio="", avatar_key="kanra",
        created_at=datetime(2026, 1, 1), password=stored_hash,
    )
    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[auth_router.get_db] = lambda: db
    app.dependency_overrides[require_gate_passed] = lambda: None
    with patch.object(auth_service, "get_user_by_username", AsyncMock(return_value=user)), patch.object(
        auth_service, "create_access_token", return_value=("test-token", 3600)
    ) as create_token:
        response = TestClient(app).post("/auth/login", json={"username": "alice", "password": password})
        if response.status_code == 401:
            create_token.assert_not_called()
        else:
            create_token.assert_called_once_with(user.id)
    return response, user, db


def test_successful_legacy_login_upgrades_password_without_exposing_it():
    legacy = hashlib.sha256(b"correct-password").hexdigest()
    response, user, db = login_with_hash(legacy, "correct-password")
    assert response.status_code == 200
    assert "password" not in response.json()["user"]
    assert user.password.startswith("pbkdf2_sha256$")
    db.commit.assert_awaited_once()


def test_wrong_legacy_password_does_not_upgrade_or_issue_token():
    legacy = hashlib.sha256(b"correct-password").hexdigest()
    response, user, db = login_with_hash(legacy, "wrong-password")
    assert response.status_code == 401
    assert user.password == legacy
    db.commit.assert_not_awaited()


@pytest.mark.parametrize("password,status", [("correct-password", 200), ("wrong-password", 401)])
def test_salted_password_login_keeps_existing_http_contract(password, status):
    salt = bytes(range(16))
    digest = hashlib.pbkdf2_hmac("sha256", b"correct-password", salt, 600_000).hex()
    stored = f"pbkdf2_sha256$600000${salt.hex()}${digest}"
    response, user, db = login_with_hash(stored, password)
    assert response.status_code == status
    assert user.password == stored
    db.commit.assert_not_awaited()


@pytest.mark.parametrize("stored", ["", "pbkdf2_sha256$bad$salt$digest", "pbkdf2_sha256$9999999999999$00$00", "密" * 64])
def test_malformed_password_hash_is_rejected(stored):
    response, user, db = login_with_hash(stored, "password")
    assert response.status_code == 401
    db.commit.assert_not_awaited()
