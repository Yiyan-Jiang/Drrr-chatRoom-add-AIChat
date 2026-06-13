from collections.abc import Awaitable, Callable

from ai.models.outbox_event import OutboxEvent


OutboxHandler = Callable[[OutboxEvent], Awaitable[None]]


class MissingOutboxHandlerError(RuntimeError):
    pass


class OutboxHandlerRegistry:
    def __init__(self):
        self._handlers: dict[str, OutboxHandler] = {}

    def register(self, event_type: str, handler: OutboxHandler) -> None:
        if not event_type or not event_type.strip():
            raise ValueError("event_type is required")
        self._handlers[event_type.strip()] = handler

    def get(self, event_type: str) -> OutboxHandler:
        try:
            return self._handlers[event_type]
        except KeyError as exc:
            raise MissingOutboxHandlerError(
                f"no outbox handler registered for event_type: {event_type}"
            ) from exc

    def list_event_types(self) -> list[str]:
        return sorted(self._handlers)


async def _noop_handler(_event: OutboxEvent) -> None:
    return None


def create_default_handler_registry() -> OutboxHandlerRegistry:
    registry = OutboxHandlerRegistry()
    for event_type in (
        "turn_completed",
        "artifact_written",
        "learning_stage_completed",
        "run_failed",
    ):
        registry.register(event_type, _noop_handler)
    return registry
