import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/chat_rooms")

from common.normal_database import Login
from normal_system.models import Friendship, Message, PrivateMessage, Room, User
from normal_system.services.message import create_message
from normal_system.services.private_message import create_private_message
from normal_system.schemas import MessageCreate


async def with_session(scenario):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Login.metadata.create_all)
        async with async_sessionmaker(engine, expire_on_commit=False)() as db:
            users = [User(username=f"user{i}", password="hashed", nickname=f"user{i}") for i in range(1, 4)]
            db.add_all(users)
            await db.flush()
            rooms = [Room(name=f"room{i}", owner_id=users[0].id) for i in range(1, 3)]
            db.add_all(rooms)
            db.add_all([
                Friendship(user_low_id=users[0].id, user_high_id=users[1].id),
                Friendship(user_low_id=users[0].id, user_high_id=users[2].id),
            ])
            await db.commit()
            await scenario(db, users, rooms)
    finally:
        await engine.dispose()


@pytest.mark.parametrize("other_user,other_room", [(True, False), (False, True)])
def test_group_message_key_cannot_return_another_user_or_room(other_user, other_room):
    async def scenario(db, users, rooms):
        await create_message(db, MessageCreate(content="original", room_id=rooms[0].id, client_message_id="group-key"), users[0].id)
        with pytest.raises(ValueError, match="client_message_id"):
            await create_message(
                db,
                MessageCreate(content="retry", room_id=rooms[int(other_room)].id, client_message_id="group-key"),
                users[int(other_user)].id,
            )

    asyncio.run(with_session(scenario))


def test_group_message_retry_in_the_same_room_returns_the_original_message():
    async def scenario(db, users, rooms):
        payload = MessageCreate(content="original", room_id=rooms[0].id, client_message_id="group-key")
        original = await create_message(db, payload, users[0].id)
        retry = await create_message(db, payload, users[0].id)
        assert retry.id == original.id

    asyncio.run(with_session(scenario))


@pytest.mark.parametrize("sender,recipient", [(1, 0), (0, 2)])
def test_private_message_key_cannot_return_another_sender_or_recipient(sender, recipient):
    async def scenario(db, users, rooms):
        await create_private_message(db, users[0].id, users[1].id, "secret", "private-key")
        with pytest.raises(ValueError, match="client_message_id"):
            await create_private_message(db, users[sender].id, users[recipient].id, "retry", "private-key")

    asyncio.run(with_session(scenario))


@pytest.mark.parametrize("private", [False, True])
@pytest.mark.parametrize("collision", [False, True])
def test_unique_key_race_recovers_only_messages_in_the_same_scope(private, collision):
    async def scenario():
        db = AsyncMock()
        db.add = lambda message: None
        db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
        if private:
            existing = PrivateMessage(id=7, sender_id=2 if collision else 1, recipient_id=3, content="original", client_message_id="key")
            with patch("normal_system.services.private_message.get_friendship", AsyncMock(return_value=object())), patch(
                "normal_system.services.private_message.get_private_message_by_client_message_id", AsyncMock(side_effect=[None, existing])
            ):
                if collision:
                    with pytest.raises(ValueError, match="client_message_id"):
                        await create_private_message(db, 1, 3, "retry", "key")
                else:
                    assert await create_private_message(db, 1, 3, "retry", "key") is existing
        else:
            existing = Message(id=7, user_id=2 if collision else 1, room_id=3, message_type="user", content="original", client_message_id="key")
            with patch("normal_system.services.message.get_room_by_id", AsyncMock(return_value=object())), patch(
                "normal_system.services.message.get_message_by_client_message_id", AsyncMock(side_effect=[None, existing])
            ):
                payload = MessageCreate(content="retry", room_id=3, client_message_id="key")
                if collision:
                    with pytest.raises(ValueError, match="client_message_id"):
                        await create_message(db, payload, 1)
                else:
                    assert await create_message(db, payload, 1) is existing
        db.rollback.assert_awaited_once()

    asyncio.run(scenario())
