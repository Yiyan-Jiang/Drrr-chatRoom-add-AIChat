import asyncio
import hashlib
import os
from unittest.mock import patch

import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")


def test_existing_http_workflows_and_permission_errors_survive_refactor():
    from app_factory import create_app
    from common.dependencies import require_gate_passed
    from common.normal_database import Login
    from normal_system.models import User
    from normal_system.routers import auth, friend, message, post, room, user

    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Login.metadata.create_all)
            async with sessions() as db:
                db.add_all([
                    User(username=name, nickname=name, password=hashlib.sha256(b"password").hexdigest())
                    for name in ("alice", "bob")
                ])
                await db.commit()

            async def get_test_db():
                async with sessions() as db:
                    yield db

            app = create_app()
            for module in (auth, friend, message, post, room, user):
                app.dependency_overrides[module.get_db] = get_test_db
            app.dependency_overrides[require_gate_passed] = lambda: None
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                denied = await client.get("/api/users/me")
                assert denied.status_code == 401
                assert denied.json() == {"detail": "Not authenticated"}

                headers = []
                for name in ("alice", "bob"):
                    login = await client.post("/api/auth/login", json={"username": name, "password": "password"})
                    assert login.status_code == 200
                    assert "password" not in login.json()["user"]
                    headers.append({"Authorization": "Bearer " + login.json()["access_token"]})

                created = await client.post("/api/rooms/", headers=headers[0], json={"name": "room1"})
                assert created.status_code == 201
                room_id = created.json()["id"]
                denied = await client.patch(f"/api/rooms/{room_id}", headers=headers[1], json={"notice": "changed"})
                assert denied.status_code == 403
                assert denied.json() == {"detail": "Only room owner can update this room"}

                payload = {"room_id": room_id, "content": "hello", "client_message_id": "contract-message"}
                sent = await client.post("/api/messages/", headers=headers[0], json=payload)
                assert sent.status_code == 201
                retry = await client.post("/api/messages/", headers=headers[0], json=payload)
                assert retry.status_code == 201
                assert retry.json() == sent.json()
                collision = await client.post("/api/messages/", headers=headers[1], json=payload)
                assert collision.status_code == 400
                assert collision.json() == {"detail": "client_message_id belongs to another conversation"}
                history = await client.get(f"/api/messages/room/{room_id}/page")
                assert history.status_code == 200
                assert [item["id"] for item in history.json()["items"]] == [sent.json()["id"]]
                assert history.json()["items"][0]["author"]["username"] == "alice"

                request = await client.post("/api/friends/requests", headers=headers[0], json={"recipient_id": 2})
                assert request.status_code == 201
                accepted = await client.post(f"/api/friends/requests/{request.json()['id']}/accept", headers=headers[1])
                assert accepted.status_code == 200
                assert accepted.json()["status"] == "accepted"
                friends = await client.get("/api/friends/", headers=headers[0])
                assert friends.status_code == 200
                assert friends.json()["total"] == 1
                assert friends.json()["items"][0]["user"]["username"] == "bob"

                created_post = await client.post("/api/posts/", headers=headers[0], json={"title": "contract-post", "content": "hello"})
                assert created_post.status_code == 201
                denied = await client.delete(f"/api/posts/{created_post.json()['id']}", headers=headers[1])
                assert denied.status_code == 403
                assert denied.json() == {"detail": "Only post author can delete this post"}
        finally:
            await engine.dispose()

    with patch.dict(os.environ, {"CHAT_JWT_SECRET": "http-behavior-test-secret-with-32-bytes"}):
        asyncio.run(scenario())
