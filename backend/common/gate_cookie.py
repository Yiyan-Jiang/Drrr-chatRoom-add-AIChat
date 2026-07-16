from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import jwt

GATE_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


def get_gate_cookie_secret() -> str:
    secret = os.environ.get("CHAT_GATE_COOKIE_SECRET") or os.environ.get("CHAT_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "CHAT_GATE_COOKIE_SECRET or CHAT_JWT_SECRET is not set. Put it in backend/.env or your shell environment."
        )
    return secret


def create_gate_cookie_value(
    *,
    secret: str | None = None,
    now: datetime | None = None,
) -> str:
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
