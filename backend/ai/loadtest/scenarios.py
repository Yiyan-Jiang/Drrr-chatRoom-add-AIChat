from dataclasses import dataclass


@dataclass(frozen=True)
class LoadTestScenario:
    name: str
    sessions: int
    turns_per_session: int
    expected_cache_hit_ratio: float = 0.0

    @property
    def total_turns(self) -> int:
        return self.sessions * self.turns_per_session

    def to_dict(self) -> dict[str, int | float | str]:
        return {
            "name": self.name,
            "sessions": self.sessions,
            "turns_per_session": self.turns_per_session,
            "total_turns": self.total_turns,
            "expected_cache_hit_ratio": self.expected_cache_hit_ratio,
        }
