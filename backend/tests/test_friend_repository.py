import asyncio
from datetime import datetime
import os

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from common.normal_database import Login
from normal_system.models import User
from normal_system.repositories.friend import (
    accept_friend_request,
    create_friend_request,
    create_private_message,
    delete_friendship,
    get_friendship,
    list_friend_requests,
    list_friends,
    list_private_messages,
)


async def run_with_session(scenario):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Login.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await scenario(session)

    await engine.dispose()


async def create_user(session, username: str) -> User:
    user = User(
        username=username,
        password="hashed",
        nickname=username,
        bio="",
        avatar_key="kanra",
        created_at=datetime.now(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def test_accept_friend_request_creates_friendship_and_lists_friend():
    async def scenario(db_session):
        alice = await create_user(db_session, "alice")
        bob = await create_user(db_session, "bob")

        request = await create_friend_request(db_session, requester_id=alice.id, recipient_id=bob.id)
        accepted = await accept_friend_request(db_session, request.id, recipient_id=bob.id)

        friendship = await get_friendship(db_session, alice.id, bob.id)
        bob_friends = await list_friends(db_session, user_id=bob.id, page=1, page_size=10)

        assert accepted.status == "accepted"
        assert friendship is not None
        assert bob_friends.total == 1
        assert bob_friends.items[0].user.id == alice.id

    asyncio.run(run_with_session(scenario))


def test_friend_request_rejects_self_existing_friend_and_duplicate_pending():
    async def scenario(db_session):
        alice = await create_user(db_session, "alice")
        bob = await create_user(db_session, "bob")

        with pytest.raises(ValueError, match="Cannot friend yourself"):
            await create_friend_request(db_session, requester_id=alice.id, recipient_id=alice.id)

        await create_friend_request(db_session, requester_id=alice.id, recipient_id=bob.id)
        with pytest.raises(ValueError, match="pending request already exists"):
            await create_friend_request(db_session, requester_id=alice.id, recipient_id=bob.id)

    asyncio.run(run_with_session(scenario))


def test_list_friend_requests_splits_incoming_and_outgoing():
    async def scenario(db_session):
        alice = await create_user(db_session, "alice")
        bob = await create_user(db_session, "bob")
        carol = await create_user(db_session, "carol")

        await create_friend_request(db_session, requester_id=alice.id, recipient_id=bob.id)
        await create_friend_request(db_session, requester_id=carol.id, recipient_id=alice.id)

        incoming = await list_friend_requests(db_session, user_id=alice.id, direction="incoming")
        outgoing = await list_friend_requests(db_session, user_id=alice.id, direction="outgoing")

        assert [item.requester.id for item in incoming.items] == [carol.id]
        assert [item.recipient.id for item in outgoing.items] == [bob.id]

    asyncio.run(run_with_session(scenario))


def test_private_messages_require_friendship_and_are_deleted_with_friendship():
    async def scenario(db_session):
        alice = await create_user(db_session, "alice")
        bob = await create_user(db_session, "bob")

        with pytest.raises(PermissionError, match="Only friends can send private messages"):
            await create_private_message(
                db_session,
                sender_id=alice.id,
                recipient_id=bob.id,
                content="hello",
                client_message_id="before-friends",
            )

        request = await create_friend_request(db_session, requester_id=alice.id, recipient_id=bob.id)
        await accept_friend_request(db_session, request.id, recipient_id=bob.id)
        message = await create_private_message(
            db_session,
            sender_id=alice.id,
            recipient_id=bob.id,
            content="hello",
            client_message_id="msg-1",
        )
        duplicate = await create_private_message(
            db_session,
            sender_id=alice.id,
            recipient_id=bob.id,
            content="hello again",
            client_message_id="msg-1",
        )
        page = await list_private_messages(db_session, user_id=bob.id, friend_id=alice.id, limit=10)

        assert duplicate.id == message.id
        assert [item.id for item in page.items] == [message.id]
        assert page.items[0].author.id == alice.id

        deleted = await delete_friendship(db_session, user_id=alice.id, friend_id=bob.id)
        after_delete = await list_private_messages(db_session, user_id=bob.id, friend_id=alice.id, limit=10)

        assert deleted is True
        assert after_delete.items == []

    asyncio.run(run_with_session(scenario))
