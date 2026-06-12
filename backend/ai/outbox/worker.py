from datetime import datetime, timedelta

from ai.outbox.handlers import OutboxHandlerRegistry
from ai.outbox.publisher import OutboxPublishResult, publish_outbox_batch


async def run_outbox_worker_once(
    worker_id: str,
    sessionmaker=None,
    handler_registry: OutboxHandlerRegistry | None = None,
    batch_size: int = 100,
    max_attempts: int = 5,
    now: datetime | None = None,
    lock_timeout: timedelta = timedelta(minutes=5),
) -> OutboxPublishResult:
    return await publish_outbox_batch(
        sessionmaker=sessionmaker,
        handler_registry=handler_registry,
        worker_id=worker_id,
        batch_size=batch_size,
        max_attempts=max_attempts,
        now=now,
        lock_timeout=lock_timeout,
    )
