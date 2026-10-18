"""签发和解析 HTTP 与 Socket.IO 共用的访问令牌。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import jwt


def get_jwt_secret() -> str:
    """读取访问令牌签名密钥；未配置时抛出 RuntimeError。"""
    secret = os.environ.get("CHAT_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "CHAT_JWT_SECRET is not set. Put it in backend/.env or your shell environment."
        )
    return secret


def get_access_token_expire_seconds() -> int:
    """读取访问令牌有效秒数，未配置时使用 3600 秒。

    Returns:
        60 到 604800 之间的有效秒数。

    Raises:
        RuntimeError: 已配置的值不是整数或超出允许范围。
    """
    raw = os.environ.get("CHAT_ACCESS_TOKEN_EXPIRE_SECONDS", "3600")
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(
            "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS 必须是 60 到 604800 之间的整数"
        ) from exc
    if not 60 <= value <= 86400 * 7:
        raise RuntimeError(
            "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS 必须是 60 到 604800 之间的整数"
        )
    return value


def create_access_token(user_id: int) -> tuple[str, int]:
    """为指定用户签发 HS256 访问令牌并返回有效秒数。"""
    ttl = get_access_token_expire_seconds()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + timedelta(seconds=ttl)},
        get_jwt_secret(),
        algorithm="HS256",
        headers={"typ": "JWT"},
    )
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token, ttl


def decode_access_token(token: str) -> int | None:
    """校验令牌签名与必需声明，返回用户 ID；无效令牌返回 None。"""
    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=["HS256"],
            options={"require": ["sub", "iat", "exp"]},
        )
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None
    try:
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return None
