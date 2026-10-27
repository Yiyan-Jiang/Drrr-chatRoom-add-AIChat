"""签发和解析 HTTP 与 Socket.IO 共用的访问令牌。"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt


def get_jwt_secret() -> str:
    """读取访问令牌签名密钥，拒绝缺失、短密钥及已知占位配置。"""
    secret = os.environ.get("CHAT_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "CHAT_JWT_SECRET is not set. Put it in backend/.env or your shell environment."
        )
    if len(secret.encode("utf-8")) < 32 or secret in {
        "dev-change-me-in-production",
        "change-me-to-a-random-secret-with-at-least-32-bytes",
    }:
        raise RuntimeError(
            "CHAT_JWT_SECRET 必须至少包含 32 个 UTF-8 字节，且不能使用默认值或示例占位值"
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
