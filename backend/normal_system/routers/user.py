from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common.dependencies import get_current_user_id
from common.normal_database import async_session
from normal_system.schemas import (
    UserCreate,
    UserInDB,
    UserProfileUpdate,
    UserPublic,
    UserUpdate,
    UserCountResponse,
)
from normal_system.repositories import (
    get_user_count,
    create_user,
    get_user_by_id,
    get_user_by_username,
    update_user,
    update_user_profile,
    delete_user,
)


router = APIRouter(prefix="/users", tags=["users"])


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/count", response_model=UserCountResponse)
async def get_count(db: AsyncSession = Depends(get_db)):
    count = await get_user_count(db)
    return {'total': count}


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
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
    user = await get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/me", response_model=UserPublic)
async def update_current_user_profile(
    profile: UserProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await update_user_profile(db, current_user_id, profile)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.get("/username/{username}", response_model=UserInDB)
async def read_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserInDB)
async def update_user_info(
        user_id: int,
        user_update: UserUpdate,
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another user")
    try:
        updated_user = await update_user(db, user_id, user_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another user")
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
