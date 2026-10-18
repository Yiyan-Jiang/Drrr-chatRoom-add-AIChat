"""计算和校验密码摘要，识别需要升级的旧版摘要。"""

import hashlib
import hmac
import secrets


_ITERATIONS = 600_000
_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """使用随机盐和 PBKDF2-SHA256 生成可存储的密码摘要。"""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_PREFIX}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验 PBKDF2 或旧版 SHA-256 摘要，格式不合法时返回 False。"""
    if not isinstance(stored, str):
        return False
    if stored.startswith(f"{_PREFIX}$"):
        try:
            _algorithm, iterations, salt_hex, digest_hex = stored.split("$")
            if iterations != str(_ITERATIONS):
                return False
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            if len(salt) != 16 or len(expected) != 32:
                return False
        except ValueError:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _ITERATIONS
        )
        return hmac.compare_digest(actual, expected)
    # 旧版 SHA-256 摘要仅在密码校验成功后升级。
    if len(stored) != 64 or not stored.isascii():
        return False
    actual = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(actual, stored)


def needs_password_upgrade(stored: str) -> bool:
    """根据摘要前缀判断是否仍使用旧版密码格式。"""
    return not stored.startswith(f"{_PREFIX}$")
