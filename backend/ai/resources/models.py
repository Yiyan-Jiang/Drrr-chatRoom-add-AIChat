from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class AgentResource:
    resource_id: str
    owner_user_id: int
    scope: Literal["turn", "session", "user", "workspace"]
    session_id: str | None
    title: str
    content: str

    def to_preview(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "title": self.title,
            "scope": self.scope,
        }

    def to_dict(self) -> dict:
        return asdict(self)
