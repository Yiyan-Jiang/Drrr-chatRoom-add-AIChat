from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.outbox_event import OutboxEvent
from ai.repositories.outbox_repository import get_outbox_event_by_event_id


@dataclass(frozen=True)
class OutboxQuery:
    status: str | None = None
    event_type: str | None = None
    aggregate_id: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = 100


async def list_outbox_events(
    db: AsyncSession,
    query: OutboxQuery | None = None,
) -> list[OutboxEvent]:
    outbox_query = query or OutboxQuery()
    records = getattr(db, "records", None)
    if records is not None:
        events = [
            event for event in records
            if isinstance(event, OutboxEvent) and _matches(event, outbox_query)
        ]
        events.sort(key=lambda event: event.created_at or datetime.min, reverse=True)
        return events[: outbox_query.limit]

    statement = select(OutboxEvent)
    if outbox_query.status:
        statement = statement.where(OutboxEvent.status == outbox_query.status)
    if outbox_query.event_type:
        statement = statement.where(OutboxEvent.event_type == outbox_query.event_type)
    if outbox_query.aggregate_id:
        statement = statement.where(OutboxEvent.aggregate_id == outbox_query.aggregate_id)
    if outbox_query.created_from:
        statement = statement.where(OutboxEvent.created_at >= outbox_query.created_from)
    if outbox_query.created_to:
        statement = statement.where(OutboxEvent.created_at <= outbox_query.created_to)
    statement = statement.order_by(OutboxEvent.created_at.desc()).limit(outbox_query.limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def summarize_outbox(db: AsyncSession) -> dict[str, int]:
    records = getattr(db, "records", None)
    if records is not None:
        summary: dict[str, int] = {}
        for event in records:
            if isinstance(event, OutboxEvent):
                summary[event.status] = summary.get(event.status, 0) + 1
        return summary

    events = await list_outbox_events(db, OutboxQuery(limit=10000))
    summary: dict[str, int] = {}
    for event in events:
        summary[event.status] = summary.get(event.status, 0) + 1
    return summary


async def get_outbox_event_detail(db: AsyncSession, event_id: str) -> dict[str, Any]:
    event = await get_outbox_event_by_event_id(db, event_id)
    if event is None:
        raise ValueError(f"Outbox event not found: {event_id}")
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "aggregate_type": event.aggregate_type,
        "aggregate_id": event.aggregate_id,
        "payload": event.payload,
        "status": event.status,
        "attempts": event.attempts,
        "next_attempt_at": event.next_attempt_at,
        "locked_at": event.locked_at,
        "locked_by": event.locked_by,
        "last_error": event.last_error,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "published_at": event.published_at,
    }


def _matches(event: OutboxEvent, query: OutboxQuery) -> bool:
    if query.status and event.status != query.status:
        return False
    if query.event_type and event.event_type != query.event_type:
        return False
    if query.aggregate_id and event.aggregate_id != query.aggregate_id:
        return False
    if query.created_from and (event.created_at is None or event.created_at < query.created_from):
        return False
    if query.created_to and (event.created_at is None or event.created_at > query.created_to):
        return False
    return True
