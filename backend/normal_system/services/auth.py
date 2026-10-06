from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from common.auth import create_access_token
from common.passwords import hash_password, needs_password_upgrade, verify_password
from normal_system.repositories.user import get_user_by_username, set_user_password
from normal_system.schemas import LoginRequest, LoginResponse, UserPublic


async def login_user(db: AsyncSession, payload: LoginRequest) -> LoginResponse | None:
    user = await get_user_by_username(db, payload.username)
    if user is None:
        return None
    if not await run_in_threadpool(verify_password, payload.password, user.password):
        return None
    if needs_password_upgrade(user.password):
        set_user_password(user, await run_in_threadpool(hash_password, payload.password))
        await db.commit()
    token, expires_in = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserPublic.model_validate(user),
    )
