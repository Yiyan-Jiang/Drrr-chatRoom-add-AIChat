from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from ai.database import get_ai_sessionmaker
from ai.models.outbox_event import OutboxEvent
from ai.outbox.dlq import move_outbox_event_to_dlq
from ai.outbox.handlers import OutboxHandlerRegistry, create_default_handler_registry
from ai.repositories.outbox_repository import calculate_backoff, claim_available_events

Publisher = Callable[[OutboxEvent], Awaitable[None]]


@dataclass(frozen=True)
class OutboxPublishResult:
    claimed: int = 0
    published: int = 0
    retried: int = 0
    dead_lettered: int = 0


async def publish_outbox_batch(
    publisher: Publisher | None = None,
    sessionmaker=None,
    worker_id: str = "outbox-worker",
    batch_size: int = 100,
    max_attempts: int = 5,
    now: datetime | None = None,
    lock_timeout: timedelta = timedelta(minutes=5),
    handler_registry: OutboxHandlerRegistry | None = None,
) -> OutboxPublishResult:
    current_time = now or datetime.now()
    session_factory = sessionmaker or get_ai_sessionmaker()
    registry = handler_registry or create_default_handler_registry()

    async with session_factory() as db:
        events = await claim_available_events(
            db=db,
            worker_id=worker_id,
            now=current_time,
            limit=batch_size,
            lock_timeout=lock_timeout,
        )
        published = 0
        retried = 0
        dead_lettered = 0

        for event in events:
            try:
                await _publish_event(event, publisher, registry)
            except Exception as exc:
                if event.attempts >= max_attempts:
                    await move_outbox_event_to_dlq(event, str(exc), now=current_time)
                    dead_lettered += 1
                else:
                    event.status = "pending"
                    event.last_error = str(exc)
                    event.next_attempt_at = current_time + calculate_backoff(event.attempts)
                    event.locked_by = None
                    event.locked_at = None
                    event.updated_at = current_time
                    retried += 1
            else:
                event.status = "published"
                event.published_at = current_time
                event.last_error = None
                event.locked_by = None
                event.locked_at = None
                event.updated_at = current_time
                published += 1

        await db.commit()
        return OutboxPublishResult(
            claimed=len(events),
            published=published,
            retried=retried,
            dead_lettered=dead_lettered,
        )


async def _publish_event(
    event: OutboxEvent,
    publisher: Publisher | None,
    registry: OutboxHandlerRegistry,
) -> None:
    if publisher is not None:
        await publisher(event)
        return
    handler = registry.get(event.event_type)
    await handler(event)
