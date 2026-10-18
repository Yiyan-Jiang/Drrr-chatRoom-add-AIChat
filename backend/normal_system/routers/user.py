"""提供账号注册、公开资料查询和本人账号操作的 HTTP 入口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.dependencies import get_current_user_id, require_gate_passed
from common.normal_database import get_db
from normal_system.schemas import (
    UserCreate,
    UserProfileUpdate,
    UserPublic,
    UserUpdate,
    UserCountResponse,
)
from normal_system.repositories import (
    get_user_count,
    get_user_by_id,
    get_user_by_username,
)
from normal_system.services.user import (
    create_user,
    update_user,
    update_user_profile,
    delete_user,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/count", response_model=UserCountResponse)
async def get_count(db: AsyncSession = Depends(get_db)):
    """返回已注册账号总数。"""
    count = await get_user_count(db)
    return {"total": count}


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_gate_passed),
):
    """注册账号并返回公开资料，用户名冲突时返回 HTTP 400。"""
    try:
        db_user = await create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserPublic)
async def read_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """返回令牌所指账号的公开资料，账号不存在时返回 HTTP 404。"""
    user = await get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/me", response_model=UserPublic)
async def update_current_user_profile(
    profile: UserProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """更新当前登录用户的个人资料并返回公开结果。"""
    updated_user = await update_user_profile(db, current_user_id, profile)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return updated_user


@router.get("/username/{username}", response_model=UserPublic)
async def read_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """按用户名返回公开资料，不存在时返回 HTTP 404。"""
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """按用户 ID 返回公开资料，不存在时返回 HTTP 404。"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """仅允许用户修改本人资料，并返回更新后的公开资料。"""
    try:
        updated_user = await update_user(
            db, user_id, user_update, requester_id=current_user_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """仅允许用户删除本人账号及其拥有的房间。"""
    try:
        success = await delete_user(db, user_id, requester_id=current_user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
