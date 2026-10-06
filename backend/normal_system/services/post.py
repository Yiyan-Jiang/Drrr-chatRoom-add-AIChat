from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models.post import Post, PostComment, PostFavorite, PostLike
from normal_system.repositories.post import (
    add_comment,
    add_post,
    add_post_reaction,
    get_post_by_id,
    get_post_comment_by_id,
    get_post_reaction_id,
    remove_post,
    remove_post_comment,
    remove_post_reaction,
)
from normal_system.schemas.post import PostCommentCreate, PostCreate


async def create_post(db: AsyncSession, payload: PostCreate, author_id: int) -> Post:
    now = datetime.now()
    post = add_post(
        db,
        title=payload.title,
        content=payload.content,
        author_id=author_id,
        status="published",
        created_at=now,
        updated_at=now,
    )
    await db.commit()
    await db.refresh(post)
    return post


async def add_post_comment(
    db: AsyncSession,
    post_id: int,
    payload: PostCommentCreate,
    author_id: int,
) -> PostComment:
    post = await get_post_by_id(db, post_id)
    if not post:
        raise ValueError("Post not found")
    now = datetime.now()
    comment = add_comment(
        db,
        post_id=post_id,
        author_id=author_id,
        content=payload.content,
        created_at=now,
        updated_at=now,
    )
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_post_comment(
    db: AsyncSession,
    post_id: int,
    comment_id: int,
    requester_id: int,
) -> bool:
    comment = await get_post_comment_by_id(db, comment_id)
    if not comment or comment.post_id != post_id:
        return False
    if comment.author_id != requester_id:
        raise PermissionError("Only comment author can delete this comment")
    await remove_post_comment(db, comment)
    await db.commit()
    return True


async def delete_post(
    db: AsyncSession,
    post_id: int,
    requester_id: int,
) -> bool:
    post = await get_post_by_id(db, post_id)
    if not post or post.status != "published":
        return False
    if post.author_id != requester_id:
        raise PermissionError("Only post author can delete this post")
    await remove_post(db, post)
    await db.commit()
    return True


async def _add_unique(db: AsyncSession, model, post_id: int, user_id: int) -> None:
    exists = await get_post_reaction_id(db, model, post_id, user_id)
    if exists is not None:
        return
    add_post_reaction(db, model, post_id, user_id, created_at=datetime.now())
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()


async def _delete_unique(db: AsyncSession, model, post_id: int, user_id: int) -> None:
    await remove_post_reaction(db, model, post_id, user_id)
    await db.commit()


async def like_post(db: AsyncSession, post_id: int, user_id: int) -> None:
    await _add_unique(db, PostLike, post_id, user_id)


async def unlike_post(db: AsyncSession, post_id: int, user_id: int) -> None:
    await _delete_unique(db, PostLike, post_id, user_id)


async def favorite_post(db: AsyncSession, post_id: int, user_id: int) -> None:
    await _add_unique(db, PostFavorite, post_id, user_id)


async def unfavorite_post(db: AsyncSession, post_id: int, user_id: int) -> None:
    await _delete_unique(db, PostFavorite, post_id, user_id)
