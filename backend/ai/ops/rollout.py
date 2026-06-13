import hashlib


def stable_bucket(subject: str, feature: str = "default") -> int:
    digest = hashlib.sha256(f"{feature}:{subject}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def is_canary_session(session_id: str, percentage: int, feature: str = "agent") -> bool:
    if percentage <= 0:
        return False
    if percentage >= 100:
        return True
    return stable_bucket(session_id, feature) < percentage
