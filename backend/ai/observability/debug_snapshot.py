from ai.evals.debug import build_debug_snapshot
from ai.models.outbox_event import OutboxEvent


def _outbox_payload(event: OutboxEvent) -> dict:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "aggregate_id": event.aggregate_id,
        "status": event.status,
        "attempts": event.attempts,
        "last_error": event.last_error,
    }


async def build_enhanced_debug_snapshot(
    repository,
    run_id: str,
    outbox_events: list[OutboxEvent] | None = None,
    cache_stats: dict | None = None,
    provider_trace: list[dict] | None = None,
    worker: list[dict] | None = None,
) -> dict:
    snapshot = await build_debug_snapshot(repository, run_id)
    snapshot["outbox"] = [_outbox_payload(event) for event in outbox_events or []]
    snapshot["cache"] = cache_stats or {"entries": 0, "hits": 0, "misses": 0}
    snapshot["provider_trace"] = provider_trace or []
    snapshot["worker"] = worker or []
    return snapshot
