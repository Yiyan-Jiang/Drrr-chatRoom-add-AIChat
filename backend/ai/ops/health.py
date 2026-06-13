from dataclasses import dataclass, field


@dataclass
class ProviderHealth:
    failures: int = 0
    successes: int = 0

    @property
    def total(self) -> int:
        return self.failures + self.successes


class ProviderHealthTracker:
    def __init__(self, max_failures: int = 3) -> None:
        self.max_failures = max_failures
        self._providers: dict[str, ProviderHealth] = {}

    def record_success(self, provider: str) -> None:
        health = self._providers.setdefault(provider, ProviderHealth())
        health.successes += 1
        health.failures = 0

    def record_failure(self, provider: str) -> None:
        health = self._providers.setdefault(provider, ProviderHealth())
        health.failures += 1

    def is_healthy(self, provider: str) -> bool:
        health = self._providers.get(provider)
        if health is None:
            return True
        return health.failures < self.max_failures

    def unhealthy_providers(self) -> list[str]:
        return [
            provider
            for provider in sorted(self._providers)
            if not self.is_healthy(provider)
        ]

    def snapshot(self) -> dict[str, dict[str, int | bool]]:
        return {
            provider: {
                "failures": health.failures,
                "successes": health.successes,
                "total": health.total,
                "healthy": self.is_healthy(provider),
            }
            for provider, health in sorted(self._providers.items())
        }
