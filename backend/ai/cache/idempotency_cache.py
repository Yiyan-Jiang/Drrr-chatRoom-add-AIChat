from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class CacheEntry:
    value: dict[str, Any]
    expires_at: datetime


class RequestResultCache:
    def __init__(self, default_ttl: timedelta):
        self._default_ttl = default_ttl
        self._entries: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def set(
        self,
        request_id: str,
        value: dict[str, Any],
        now: datetime | None = None,
        ttl: timedelta | None = None,
    ) -> None:
        current_time = now or datetime.now()
        self._entries[request_id] = CacheEntry(
            value=value,
            expires_at=current_time + (ttl or self._default_ttl),
        )

    def get(self, request_id: str, now: datetime | None = None) -> dict[str, Any] | None:
        current_time = now or datetime.now()
        entry = self._entries.get(request_id)
        if entry is None:
            self._misses += 1
            return None
        if entry.expires_at <= current_time:
            self._entries.pop(request_id, None)
            self._misses += 1
            return None
        self._hits += 1
        return entry.value

    def stats(self) -> dict[str, int]:
        return {
            "entries": len(self._entries),
            "hits": self._hits,
            "misses": self._misses,
        }
