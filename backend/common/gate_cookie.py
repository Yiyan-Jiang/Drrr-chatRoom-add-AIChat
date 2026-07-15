from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os


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
    payload = {
        "passed": True,
        "exp": int((actual_now + timedelta(seconds=GATE_COOKIE_MAX_AGE_SECONDS)).timestamp()),
    }
    payload_segment = _base64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = _sign(payload_segment, actual_secret)
    return f"{payload_segment}.{signature}"


def is_gate_cookie_valid(
    cookie_value: str | None,
    *,
    secret: str | None = None,
    now: datetime | None = None,
) -> bool:
    if not cookie_value:
        return False

    payload_segment, separator, signature = cookie_value.partition(".")
    if not separator or not payload_segment or not signature:
        return False

    actual_secret = secret or get_gate_cookie_secret()
    expected_signature = _sign(payload_segment, actual_secret)
    if not hmac.compare_digest(signature, expected_signature):
        return False

    try:
        payload = json.loads(_base64url_decode(payload_segment).decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return False

    try:
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return False

    actual_now = now or datetime.now(timezone.utc)
    return payload.get("passed") is True and expires_at > int(actual_now.timestamp())


def _sign(payload_segment: str, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(digest)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
