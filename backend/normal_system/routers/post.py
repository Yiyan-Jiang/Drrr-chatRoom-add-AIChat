"""提供帖子、评论、点赞和收藏的 HTTP 入口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.dependencies import get_current_user_id
from common.normal_database import get_db
from normal_system.services.post import (
    add_post_comment,
    create_post,
    delete_post,
    delete_post_comment,
    favorite_post,
    like_post,
    unfavorite_post,
    unlike_post,
)
from normal_system.repositories.post import (
    get_post_detail,
    list_my_favorite_posts,
    list_my_liked_posts,
    list_my_post_comments,
    list_my_posts,
    list_post_comments,
    list_posts,
)
from normal_system.schemas import (
    PaginatedCommentsResponse,
    PaginatedMyCommentsResponse,
    PaginatedPostsResponse,
    PostCommentCreate,
    PostCommentInDB,
    PostCreate,
    PostDetail,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PaginatedPostsResponse)
async def list_posts_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
    friends_only: bool = Query(False),
):
    """返回已发布帖子页，按需限定为当前登录用户的好友动态。"""
    return await list_posts(
        db, viewer_id=user_id, limit=limit, cursor=cursor, friends_only=friends_only
    )


@router.post("/", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
async def create_post_endpoint(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """发布帖子并返回正文、作者与互动状态。"""
    post = await create_post(db, payload, author_id=user_id)
    detail = await get_post_detail(db, post.id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Post was not created",
        )
    return detail


@router.get("/favorites/mine", response_model=PaginatedPostsResponse)
async def list_my_favorite_posts_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
):
    """返回当前登录用户收藏的帖子页。"""
    return await list_my_favorite_posts(db, user_id=user_id, limit=limit, cursor=cursor)


@router.get("/mine", response_model=PaginatedPostsResponse)
async def list_my_posts_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
):
    """返回当前登录用户发布的帖子页。"""
    return await list_my_posts(db, user_id=user_id, limit=limit, cursor=cursor)


@router.get("/likes/mine", response_model=PaginatedPostsResponse)
async def list_my_liked_posts_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
):
    """返回当前登录用户点赞的帖子页。"""
    return await list_my_liked_posts(db, user_id=user_id, limit=limit, cursor=cursor)


@router.get("/comments/mine", response_model=PaginatedMyCommentsResponse)
async def list_my_post_comments_endpoint(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
):
    """返回当前登录用户的评论及关联帖子预览。"""
    return await list_my_post_comments(db, user_id=user_id, limit=limit, cursor=cursor)


@router.get("/{post_id:int}", response_model=PostDetail)
async def get_post_detail_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """返回已发布帖子的完整展示数据，不存在时返回 HTTP 404。"""
    detail = await get_post_detail(db, post_id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return detail


@router.delete("/{post_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """校验作者身份后删除帖子，非作者返回 HTTP 403。"""
    try:
        deleted = await delete_post(db, post_id, requester_id=user_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )


@router.get("/{post_id:int}/comments", response_model=PaginatedCommentsResponse)
async def list_post_comments_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
    limit: int = Query(30, ge=1, le=50),
    cursor: int | None = Query(default=None, ge=1),
):
    """向登录用户返回指定帖子的评论页。"""
    return await list_post_comments(db, post_id=post_id, limit=limit, cursor=cursor)


@router.post(
    "/{post_id:int}/comments",
    response_model=PostCommentInDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_post_comment_endpoint(
    post_id: int,
    payload: PostCommentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """为指定帖子创建当前用户的评论并返回公开资料。"""
    try:
        comment = await add_post_comment(db, post_id, payload, author_id=user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    comments = await list_post_comments(db, post_id=post_id, limit=1)
    return next(item for item in comments.items if item.id == comment.id)


@router.delete(
    "/{post_id:int}/comments/{comment_id:int}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post_comment_endpoint(
    post_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """校验作者身份后删除指定帖子内的评论。"""
    try:
        deleted = await delete_post_comment(
            db, post_id, comment_id, requester_id=user_id
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )


@router.put("/{post_id:int}/like", response_model=PostDetail)
async def like_post_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """登记当前用户的点赞并返回帖子详情。"""
    await like_post(db, post_id, user_id)
    detail = await get_post_detail(db, post_id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return detail


@router.delete("/{post_id:int}/like", response_model=PostDetail)
async def unlike_post_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """删除当前用户的点赞并返回帖子详情。"""
    await unlike_post(db, post_id, user_id)
    detail = await get_post_detail(db, post_id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return detail


@router.put("/{post_id:int}/favorite", response_model=PostDetail)
async def favorite_post_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """登记当前用户的收藏并返回帖子详情。"""
    await favorite_post(db, post_id, user_id)
    detail = await get_post_detail(db, post_id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return detail


@router.delete("/{post_id:int}/favorite", response_model=PostDetail)
async def unfavorite_post_endpoint(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """删除当前用户的收藏并返回帖子详情。"""
    await unfavorite_post(db, post_id, user_id)
    detail = await get_post_detail(db, post_id, viewer_id=user_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return detail
