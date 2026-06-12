from datetime import datetime

from ai.models.outbox_event import OutboxEvent


async def move_outbox_event_to_dlq(
    event: OutboxEvent,
    error_message: str,
    now: datetime | None = None,
) -> OutboxEvent:
    current_time = now or datetime.now()
    event.status = "dead"
    event.last_error = error_message
    event.locked_by = None
    event.locked_at = None
    event.updated_at = current_time
    return event
