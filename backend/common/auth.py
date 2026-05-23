from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import time


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


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(segment: str) -> bytes:
    pad = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + pad)


def create_access_token(user_id: int) -> tuple[str, int]:
    secret = get_jwt_secret()
    now = int(time.time())
    ttl = get_access_token_expire_seconds()
    payload = {"sub": user_id, "iat": now, "exp": now + ttl}
    body = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}", ttl


def decode_access_token(token: str) -> int | None:
    try:
        body_b64, sig_hex = token.rsplit(".", 1)
    except ValueError:
        return None
    secret = get_jwt_secret()
    expected = hmac.new(secret.encode("utf-8"), body_b64.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig_hex):
        return None
    try:
        payload = json.loads(_b64url_decode(body_b64).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, binascii.Error, ValueError):
        return None
    try:
        exp = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return None
    if int(time.time()) > exp:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return None
