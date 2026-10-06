from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from normal_system.models import User
from normal_system.models.post import Post, PostComment, PostFavorite, PostLike
from normal_system.schemas.post import (
    PaginatedCommentsResponse,
    PaginatedMyCommentsResponse,
    PaginatedPostsResponse,
    PostCommentInDB,
    PostCommentListItem,
    PostDetail,
    PostListItem,
)
from normal_system.schemas.user import UserPublic


def _preview(content: str, limit: int = 180) -> str:
    return content[:limit]


def _author_public(user: User | None) -> UserPublic | None:
    return UserPublic.model_validate(user) if user else None


async def _post_counts(db: AsyncSession, post_id: int) -> tuple[int, int, int]:
    comments = await db.scalar(
        select(func.count()).select_from(PostComment).where(PostComment.post_id == post_id)
    )
    likes = await db.scalar(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
    )
    favorites = await db.scalar(
        select(func.count()).select_from(PostFavorite).where(PostFavorite.post_id == post_id)
    )
    return int(comments or 0), int(likes or 0), int(favorites or 0)


async def _viewer_flags(db: AsyncSession, post_id: int, viewer_id: int | None) -> tuple[bool, bool]:
    if viewer_id is None:
        return False, False
    liked = await db.scalar(
        select(PostLike.id).where(PostLike.post_id == post_id, PostLike.user_id == viewer_id)
    )
    favorited = await db.scalar(
        select(PostFavorite.id).where(
            PostFavorite.post_id == post_id,
            PostFavorite.user_id == viewer_id,
        )
    )
    return liked is not None, favorited is not None


async def list_post_comments(
    db: AsyncSession,
    post_id: int,
    limit: int = 30,
    cursor: int | None = None,
) -> PaginatedCommentsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [PostComment.post_id == post_id]
    if cursor is not None:
        filters.append(PostComment.id < cursor)
    result = await db.execute(
        select(PostComment, User)
        .outerjoin(User, PostComment.author_id == User.id)
        .where(*filters)
        .order_by(PostComment.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        PostCommentInDB(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            author=_author_public(author),
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
        for comment, author in page_rows
    ]
    return PaginatedCommentsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def _to_list_item(db: AsyncSession, post: Post, author: User | None, viewer_id: int | None) -> PostListItem:
    comments, likes, favorites = await _post_counts(db, post.id)
    liked, _favorited = await _viewer_flags(db, post.id, viewer_id)
    return PostListItem(
        id=post.id,
        title=post.title,
        content_preview=_preview(post.content),
        author=_author_public(author),
        comments_count=comments,
        likes_count=likes,
        favorites_count=favorites,
        liked_by_me=liked,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


async def list_posts(
    db: AsyncSession,
    viewer_id: int | None,
    limit: int = 20,
    cursor: int | None = None,
) -> PaginatedPostsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [Post.status == "published"]
    if cursor is not None:
        filters.append(Post.id < cursor)
    result = await db.execute(
        select(Post, User)
        .outerjoin(User, Post.author_id == User.id)
        .where(*filters)
        .order_by(Post.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        await _to_list_item(db, post, author, viewer_id)
        for post, author in page_rows
    ]
    return PaginatedPostsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def get_post_detail(
    db: AsyncSession,
    post_id: int,
    viewer_id: int | None,
) -> PostDetail | None:
    result = await db.execute(
        select(Post, User)
        .outerjoin(User, Post.author_id == User.id)
        .where(Post.id == post_id, Post.status == "published")
    )
    row = result.one_or_none()
    if row is None:
        return None
    post, author = row
    comments, likes, favorites = await _post_counts(db, post.id)
    liked, favorited = await _viewer_flags(db, post.id, viewer_id)
    return PostDetail(
        id=post.id,
        title=post.title,
        content_preview=_preview(post.content),
        content=post.content,
        author=_author_public(author),
        comments_count=comments,
        likes_count=likes,
        favorites_count=favorites,
        liked_by_me=liked,
        favorited_by_me=favorited,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


async def list_my_favorite_posts(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    cursor: int | None = None,
) -> PaginatedPostsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [PostFavorite.user_id == user_id, Post.status == "published"]
    if cursor is not None:
        filters.append(Post.id < cursor)
    result = await db.execute(
        select(Post, User)
        .join(PostFavorite, PostFavorite.post_id == Post.id)
        .outerjoin(User, Post.author_id == User.id)
        .where(*filters)
        .order_by(PostFavorite.created_at.desc(), Post.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        await _to_list_item(db, post, author, user_id)
        for post, author in page_rows
    ]
    return PaginatedPostsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def list_my_posts(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    cursor: int | None = None,
) -> PaginatedPostsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [Post.author_id == user_id, Post.status == "published"]
    if cursor is not None:
        filters.append(Post.id < cursor)
    result = await db.execute(
        select(Post, User)
        .outerjoin(User, Post.author_id == User.id)
        .where(*filters)
        .order_by(Post.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        await _to_list_item(db, post, author, user_id)
        for post, author in page_rows
    ]
    return PaginatedPostsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def list_my_liked_posts(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    cursor: int | None = None,
) -> PaginatedPostsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [PostLike.user_id == user_id, Post.status == "published"]
    if cursor is not None:
        filters.append(Post.id < cursor)
    result = await db.execute(
        select(Post, User)
        .join(PostLike, PostLike.post_id == Post.id)
        .outerjoin(User, Post.author_id == User.id)
        .where(*filters)
        .order_by(PostLike.created_at.desc(), Post.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        await _to_list_item(db, post, author, user_id)
        for post, author in page_rows
    ]
    return PaginatedPostsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def list_my_post_comments(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    cursor: int | None = None,
) -> PaginatedMyCommentsResponse:
    safe_limit = max(1, min(limit, 50))
    filters = [PostComment.author_id == user_id, Post.status == "published"]
    if cursor is not None:
        filters.append(PostComment.id < cursor)
    result = await db.execute(
        select(PostComment, Post, User)
        .join(Post, PostComment.post_id == Post.id)
        .outerjoin(User, PostComment.author_id == User.id)
        .where(*filters)
        .order_by(PostComment.id.desc())
        .limit(safe_limit + 1)
    )
    rows = result.all()
    page_rows = rows[:safe_limit]
    items = [
        PostCommentListItem(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            author=_author_public(author),
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            post_title=post.title,
            post_content_preview=_preview(post.content),
        )
        for comment, post, author in page_rows
    ]
    return PaginatedMyCommentsResponse(
        items=items,
        has_more=len(rows) > safe_limit,
        next_cursor=items[-1].id if len(rows) > safe_limit and items else None,
    )


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    return await db.get(Post, post_id)


async def get_post_comment_by_id(db: AsyncSession, comment_id: int) -> PostComment | None:
    return await db.get(PostComment, comment_id)


def add_post(db: AsyncSession, **fields) -> Post:
    post = Post(**fields)
    db.add(post)
    return post


def add_comment(db: AsyncSession, **fields) -> PostComment:
    comment = PostComment(**fields)
    db.add(comment)
    return comment


async def remove_post(db: AsyncSession, post: Post) -> None:
    await db.delete(post)


async def remove_post_comment(db: AsyncSession, comment: PostComment) -> None:
    await db.delete(comment)


async def get_post_reaction_id(db: AsyncSession, model, post_id: int, user_id: int) -> int | None:
    return await db.scalar(select(model.id).where(model.post_id == post_id, model.user_id == user_id))


def add_post_reaction(db: AsyncSession, model, post_id: int, user_id: int, *, created_at: datetime) -> None:
    db.add(model(post_id=post_id, user_id=user_id, created_at=created_at))


async def remove_post_reaction(db: AsyncSession, model, post_id: int, user_id: int) -> None:
    await db.execute(delete(model).where(model.post_id == post_id, model.user_id == user_id))
