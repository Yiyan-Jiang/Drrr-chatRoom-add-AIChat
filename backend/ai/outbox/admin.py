from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.outbox_event import OutboxEvent
from ai.repositories.outbox_repository import get_outbox_event_by_event_id


async def requeue_dead_event(
    db: AsyncSession,
    event_id: str,
    reset_attempts: bool = False,
    now: datetime | None = None,
) -> OutboxEvent:
    event = await _load_recoverable_event(db, event_id)
    current_time = now or datetime.now()
    event.status = "pending"
    event.next_attempt_at = current_time
    event.locked_by = None
    event.locked_at = None
    if reset_attempts:
        event.attempts = 0
    event.updated_at = current_time
    await db.commit()
    return event


async def abandon_dead_event(
    db: AsyncSession,
    event_id: str,
    reason: str,
    now: datetime | None = None,
) -> OutboxEvent:
    event = await _load_recoverable_event(db, event_id)
    current_time = now or datetime.now()
    event.status = "abandoned"
    event.locked_by = None
    event.locked_at = None
    previous_error = event.last_error or ""
    reason_text = reason.strip() if reason else "abandoned"
    event.last_error = (
        f"{previous_error}; abandoned: {reason_text}"
        if previous_error
        else f"abandoned: {reason_text}"
    )
    event.updated_at = current_time
    await db.commit()
    return event


async def _load_recoverable_event(db: AsyncSession, event_id: str) -> OutboxEvent:
    event = await get_outbox_event_by_event_id(db, event_id)
    if event is None:
        raise ValueError(f"Outbox event not found: {event_id}")
    if event.status not in {"dead", "failed"}:
        raise ValueError(f"Outbox event is not recoverable: {event_id}")
    return event
