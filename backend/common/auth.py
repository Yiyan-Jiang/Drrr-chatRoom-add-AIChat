from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import jwt


def get_jwt_secret() -> str:
    secret = os.environ.get("CHAT_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "CHAT_JWT_SECRET is not set. Put it in backend/.env or your shell environment."
        )
    return secret


def get_access_token_expire_seconds() -> int:
    raw = os.environ.get("CHAT_ACCESS_TOKEN_EXPIRE_SECONDS", "3600")
    try:
        value = int(raw)
    except ValueError:
        return 3600
    return max(60, min(value, 86400 * 7))


def create_access_token(user_id: int) -> tuple[str, int]:
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
