from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from common.auth import create_access_token
from common.passwords import hash_password, needs_password_upgrade, verify_password
from common.dependencies import require_gate_passed
from common.normal_database import async_session
from normal_system.repositories import get_user_by_username
from normal_system.schemas import LoginRequest, LoginResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_gate_passed),
):
    user = await get_user_by_username(db, payload.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not await run_in_threadpool(verify_password, payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if needs_password_upgrade(user.password):
        user.password = await run_in_threadpool(hash_password, payload.password)
        await db.commit()
    # 用用户 ID 生成 JWT，返回令牌字符串和过期时间（秒）
    token, expires_in = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserPublic.model_validate(user),
    )
