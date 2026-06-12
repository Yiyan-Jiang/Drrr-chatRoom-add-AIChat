from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.outbox_event import OutboxEvent


def new_event_id() -> str:
    return str(uuid4())


def calculate_backoff(attempts: int) -> timedelta:
    seconds = min(60, 2**attempts)
    return timedelta(seconds=seconds)


def _session_records(db) -> list[OutboxEvent] | None:
    records = getattr(db, "records", None)
    if records is None:
        return None
    return [record for record in records if isinstance(record, OutboxEvent)]


def _find_outbox_record(db, event_id: str) -> OutboxEvent | None:
    records = _session_records(db)
    if records is None:
        return None
    for record in records:
        if record.event_id == event_id:
            return record
    return None


async def create_outbox_event(
    db: AsyncSession,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    now: datetime | None = None,
) -> OutboxEvent:
    current_time = now or datetime.now()
    event = OutboxEvent(
        event_id=new_event_id(),
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        status="pending",
        attempts=0,
        next_attempt_at=current_time,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(event)
    await db.flush()
    return event


async def claim_pending_events(
    db: AsyncSession,
    worker_id: str,
    now: datetime | None = None,
    limit: int = 100,
) -> list[OutboxEvent]:
    return await claim_available_events(
        db=db,
        worker_id=worker_id,
        now=now,
        limit=limit,
    )


async def claim_available_events(
    db: AsyncSession,
    worker_id: str,
    now: datetime | None = None,
    limit: int = 100,
    lock_timeout: timedelta = timedelta(minutes=5),
) -> list[OutboxEvent]:
    current_time = now or datetime.now()
    expired_before = current_time - lock_timeout
    records = _session_records(db)
    if records is not None:
        events = [
            event
            for event in records
            if _is_claimable(event, current_time, expired_before)
        ]
        events.sort(key=lambda event: event.created_at or current_time)
        events = events[:limit]
    else:
        result = await db.execute(
            select(OutboxEvent)
            .where(
                or_(
                    (OutboxEvent.status == "pending")
                    & (OutboxEvent.next_attempt_at <= current_time),
                    (OutboxEvent.status == "locked")
                    & (OutboxEvent.locked_at < expired_before),
                )
            )
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        events = list(result.scalars().all())

    for event in events:
        event.status = "locked"
        event.locked_by = worker_id
        event.locked_at = current_time
        event.attempts += 1
        event.updated_at = current_time

    await db.commit()
    return events


def _is_claimable(
    event: OutboxEvent,
    current_time: datetime,
    expired_before: datetime,
) -> bool:
    if event.status == "pending":
        return event.next_attempt_at is None or event.next_attempt_at <= current_time
    if event.status == "locked":
        return event.locked_at is not None and event.locked_at < expired_before
    return False


async def get_outbox_event_by_event_id(
    db: AsyncSession,
    event_id: str,
) -> OutboxEvent | None:
    fake_record = _find_outbox_record(db, event_id)
    if fake_record is not None:
        return fake_record
    result = await db.execute(
        select(OutboxEvent).where(OutboxEvent.event_id == event_id)
    )
    return result.scalar_one_or_none()


async def mark_event_published(
    db: AsyncSession,
    event_id: str,
    now: datetime | None = None,
) -> OutboxEvent:
    event = await get_outbox_event_by_event_id(db, event_id)
    if event is None:
        raise ValueError(f"Outbox event not found: {event_id}")

    current_time = now or datetime.now()
    event.status = "published"
    event.published_at = current_time
    event.last_error = None
    event.locked_by = None
    event.locked_at = None
    event.updated_at = current_time
    await db.commit()
    return event


async def mark_event_retry(
    db: AsyncSession,
    event_id: str,
    error_message: str,
    now: datetime | None = None,
) -> OutboxEvent:
    event = await get_outbox_event_by_event_id(db, event_id)
    if event is None:
        raise ValueError(f"Outbox event not found: {event_id}")

    current_time = now or datetime.now()
    event.status = "pending"
    event.last_error = error_message
    event.next_attempt_at = current_time + calculate_backoff(event.attempts)
    event.locked_by = None
    event.locked_at = None
    event.updated_at = current_time
    await db.commit()
    return event


async def mark_event_failed(
    db: AsyncSession,
    event_id: str,
    error_message: str,
    now: datetime | None = None,
) -> OutboxEvent:
    event = await get_outbox_event_by_event_id(db, event_id)
    if event is None:
        raise ValueError(f"Outbox event not found: {event_id}")

    current_time = now or datetime.now()
    event.status = "dead"
    event.last_error = error_message
    event.locked_by = None
    event.locked_at = None
    event.updated_at = current_time
    await db.commit()
    return event
