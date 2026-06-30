import asyncio
from datetime import datetime
import os

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from common.normal_database import Login
from normal_system.models import User
from normal_system.repositories.post import (
    add_post_comment,
    create_post,
    favorite_post,
    get_post_detail,
    list_my_favorite_posts,
    list_my_liked_posts,
    list_my_post_comments,
    list_my_posts,
    list_posts,
    like_post,
    unfavorite_post,
    unlike_post,
)
from normal_system.schemas.post import PostCommentCreate, PostCreate


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


def test_post_detail_includes_author_counts_and_current_user_state():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")

        post = await create_post(
            db_session,
            PostCreate(title="Hello posts", content="**markdown** body"),
            author_id=author.id,
        )
        await add_post_comment(
            db_session,
            post.id,
            PostCommentCreate(content="first comment"),
            author_id=viewer.id,
        )
        await like_post(db_session, post.id, viewer.id)
        await like_post(db_session, post.id, viewer.id)
        await favorite_post(db_session, post.id, viewer.id)
        await favorite_post(db_session, post.id, viewer.id)

        detail = await get_post_detail(db_session, post.id, viewer.id)

        assert detail is not None
        assert detail.title == "Hello posts"
        assert detail.author is not None
        assert detail.author.id == author.id
        assert detail.comments_count == 1
        assert detail.likes_count == 1
        assert detail.favorites_count == 1
        assert detail.liked_by_me is True
        assert detail.favorited_by_me is True

    asyncio.run(run_with_session(scenario))


def test_list_posts_omits_favorited_state_but_includes_counts():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")
        post = await create_post(
            db_session,
            PostCreate(title="List me", content="body"),
            author_id=author.id,
        )
        await like_post(db_session, post.id, viewer.id)
        await favorite_post(db_session, post.id, viewer.id)

        page = await list_posts(db_session, viewer.id, limit=10)

        assert len(page.items) == 1
        item = page.items[0]
        assert item.id == post.id
        assert item.likes_count == 1
        assert item.favorites_count == 1
        assert item.liked_by_me is True
        assert not hasattr(item, "favorited_by_me")

    asyncio.run(run_with_session(scenario))


def test_list_posts_preview_preserves_markdown_line_breaks():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        post = await create_post(
            db_session,
            PostCreate(title="Markdown preview", content="## 标题\n\n- 第一项\n- 第二项"),
            author_id=author.id,
        )

        page = await list_posts(db_session, author.id, limit=10)

        assert page.items[0].id == post.id
        assert page.items[0].content_preview == "## 标题\n\n- 第一项\n- 第二项"

    asyncio.run(run_with_session(scenario))


def test_my_favorites_returns_current_user_favorited_posts():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")
        favorite = await create_post(
            db_session,
            PostCreate(title="Saved", content="body"),
            author_id=author.id,
        )
        other = await create_post(
            db_session,
            PostCreate(title="Not saved", content="body"),
            author_id=author.id,
        )

        await favorite_post(db_session, favorite.id, viewer.id)
        await favorite_post(db_session, other.id, author.id)

        page = await list_my_favorite_posts(db_session, viewer.id, limit=10)

        assert [post.id for post in page.items] == [favorite.id]

    asyncio.run(run_with_session(scenario))


def test_my_posts_returns_current_user_published_posts():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")
        mine = await create_post(
            db_session,
            PostCreate(title="Mine", content="body"),
            author_id=viewer.id,
        )
        await create_post(
            db_session,
            PostCreate(title="Not mine", content="body"),
            author_id=author.id,
        )

        page = await list_my_posts(db_session, user_id=viewer.id, limit=10)

        assert [post.id for post in page.items] == [mine.id]

    asyncio.run(run_with_session(scenario))


def test_my_likes_returns_current_user_liked_posts():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")
        liked = await create_post(
            db_session,
            PostCreate(title="Liked", content="body"),
            author_id=author.id,
        )
        other = await create_post(
            db_session,
            PostCreate(title="Not liked", content="body"),
            author_id=author.id,
        )

        await like_post(db_session, liked.id, viewer.id)
        await like_post(db_session, other.id, author.id)

        page = await list_my_liked_posts(db_session, user_id=viewer.id, limit=10)

        assert [post.id for post in page.items] == [liked.id]

    asyncio.run(run_with_session(scenario))


def test_my_comments_returns_current_user_comments_with_post_summary():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        viewer = await create_user(db_session, "bob")
        saved_post = await create_post(
            db_session,
            PostCreate(title="Commented post", content="body"),
            author_id=author.id,
        )
        other_post = await create_post(
            db_session,
            PostCreate(title="Other post", content="body"),
            author_id=author.id,
        )

        mine = await add_post_comment(
            db_session,
            saved_post.id,
            PostCommentCreate(content="my comment"),
            author_id=viewer.id,
        )
        await add_post_comment(
            db_session,
            other_post.id,
            PostCommentCreate(content="someone else"),
            author_id=author.id,
        )

        page = await list_my_post_comments(db_session, user_id=viewer.id, limit=10)

        assert len(page.items) == 1
        item = page.items[0]
        assert item.id == mine.id
        assert item.content == "my comment"
        assert item.post_id == saved_post.id
        assert item.post_title == "Commented post"
        assert item.post_content_preview == "body"

    asyncio.run(run_with_session(scenario))


def test_like_and_favorite_delete_are_idempotent():
    async def scenario(db_session):
        author = await create_user(db_session, "alice")
        post = await create_post(
            db_session,
            PostCreate(title="Toggle", content="body"),
            author_id=author.id,
        )

        await like_post(db_session, post.id, author.id)
        await unlike_post(db_session, post.id, author.id)
        await unlike_post(db_session, post.id, author.id)
        await favorite_post(db_session, post.id, author.id)
        await unfavorite_post(db_session, post.id, author.id)
        await unfavorite_post(db_session, post.id, author.id)

        detail = await get_post_detail(db_session, post.id, author.id)

        assert detail is not None
        assert detail.likes_count == 0
        assert detail.favorites_count == 0
        assert detail.liked_by_me is False
        assert detail.favorited_by_me is False

    asyncio.run(run_with_session(scenario))
