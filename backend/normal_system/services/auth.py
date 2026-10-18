"""校验登录密码、升级旧摘要并签发访问令牌。"""

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from common.auth import create_access_token
from common.passwords import hash_password, needs_password_upgrade, verify_password
from normal_system.repositories.user import get_user_by_username, set_user_password
from normal_system.schemas import LoginRequest, LoginResponse, UserPublic


async def login_user(db: AsyncSession, payload: LoginRequest) -> LoginResponse | None:
    """校验密码、按需升级旧摘要，并为登录成功的账号签发令牌。

    Args:
        db: 查询账号和提交密码摘要升级所使用的数据库会话。
        payload: 用户输入的用户名和明文密码。

    Returns:
        包含公开用户资料、访问令牌和有效秒数的登录结果；凭证错误时为 None。
    """
    user = await get_user_by_username(db, payload.username)
    if user is None:
        return None
    if not await run_in_threadpool(verify_password, payload.password, user.password):
        return None
    if needs_password_upgrade(user.password):
        set_user_password(
            user, await run_in_threadpool(hash_password, payload.password)
        )
        await db.commit()
    token, expires_in = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserPublic.model_validate(user),
    )
