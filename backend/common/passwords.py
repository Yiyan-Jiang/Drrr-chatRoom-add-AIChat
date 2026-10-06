import hashlib
import hmac
import secrets


_ITERATIONS = 600_000
_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_PREFIX}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
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
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
        return hmac.compare_digest(actual, expected)
    # Legacy SHA-256 hashes are upgraded only after a successful login.
    if len(stored) != 64 or not stored.isascii():
        return False
    actual = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(actual, stored)


def needs_password_upgrade(stored: str) -> bool:
    return not stored.startswith(f"{_PREFIX}$")
