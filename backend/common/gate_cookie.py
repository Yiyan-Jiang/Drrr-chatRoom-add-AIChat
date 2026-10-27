"""签发和验证带过期时间的门禁 Cookie。"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

GATE_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


def get_gate_cookie_secret() -> str:
    """读取独立的门禁签名密钥，拒绝缺失、短密钥及已知占位配置。"""
    secret = os.environ.get("CHAT_GATE_COOKIE_SECRET")
    if not secret:
        raise RuntimeError(
            "CHAT_GATE_COOKIE_SECRET is not set. Put it in backend/.env or your shell environment."
        )
    if len(secret.encode("utf-8")) < 32 or secret in {
        "dev-change-me-in-production",
        "change-me-to-a-random-secret-with-at-least-32-bytes",
    }:
        raise RuntimeError(
            "CHAT_GATE_COOKIE_SECRET 必须至少包含 32 个 UTF-8 字节，且不能使用默认值或示例占位值"
        )
    return secret


def create_gate_cookie_value(
    *,
    secret: str | None = None,
    now: datetime | None = None,
) -> str:
    """签发七天有效、带有门禁通过标记的 Cookie 值。

    Args:
        secret: 显式签名密钥；未提供时读取后端环境配置。
        now: 签发时间；未提供时使用当前 UTC 时间。

    Returns:
        使用 HS256 签名的门禁 JWT 字符串。
    """
    actual_secret = secret or get_gate_cookie_secret()
    actual_now = now or datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "typ": "gate",
            "passed": True,
            "iat": actual_now,
            "exp": actual_now + timedelta(seconds=GATE_COOKIE_MAX_AGE_SECONDS),
        },
        actual_secret,
        algorithm="HS256",
        headers={"typ": "JWT"},
    )
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# 校验 cookie 是否被篡改
def is_gate_cookie_valid(
    cookie_value: str | None,
    *,
    secret: str | None = None,
    now: datetime | None = None,
) -> bool:
    """校验门禁 Cookie 的签名、必需声明和过期时间。

    Args:
        cookie_value: 请求携带的 Cookie，缺失时验证失败。
        secret: 显式校验密钥；未提供时读取后端环境配置。
        now: 用于过期比较的时间；未提供时使用当前 UTC 时间。

    Returns:
        Cookie 包含正确门禁标记且未过期时为 True。
    """
    if not cookie_value:
        return False

    actual_secret = secret or get_gate_cookie_secret()
    try:
        payload = jwt.decode(
            cookie_value,
            actual_secret,
            algorithms=["HS256"],
            options={
                "require": ["typ", "passed", "iat", "exp"],
                "verify_exp": now is None,
            },
        )
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return False

    if payload.get("typ") != "gate" or payload.get("passed") is not True:
        return False

    actual_now = now or datetime.now(timezone.utc)
    try:
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return False
    return expires_at > int(actual_now.timestamp())
