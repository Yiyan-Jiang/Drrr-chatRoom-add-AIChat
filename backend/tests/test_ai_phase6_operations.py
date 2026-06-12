import unittest
from datetime import datetime, timedelta

from ai.models.outbox_event import OutboxEvent


class FakeSession:
    def __init__(self, records=None):
        self.records = records or []
        self.commits = 0

    async def commit(self):
        self.commits += 1


class FakeSessionFactory:
    def __init__(self, session):
        self.session = session

    def __call__(self):
        return self

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


class Phase6OutboxPublisherTest(unittest.IsolatedAsyncioTestCase):
    async def test_claim_available_events_skips_future_and_reclaims_expired_locks(self):
        from ai.repositories.outbox_repository import claim_available_events

        now = datetime(2026, 5, 26, 12, 0, 0)
        due = OutboxEvent(
            event_id="due",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=now - timedelta(seconds=1),
            created_at=now - timedelta(minutes=3),
        )
        future = OutboxEvent(
            event_id="future",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-2",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=now + timedelta(minutes=5),
            created_at=now - timedelta(minutes=2),
        )
        fresh_locked = OutboxEvent(
            event_id="fresh-locked",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-3",
            payload={},
            status="locked",
            attempts=1,
            locked_at=now - timedelta(seconds=10),
            locked_by="worker-old",
            created_at=now - timedelta(minutes=1),
        )
        expired_locked = OutboxEvent(
            event_id="expired-locked",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-4",
            payload={},
            status="locked",
            attempts=2,
            locked_at=now - timedelta(minutes=10),
            locked_by="worker-old",
            created_at=now - timedelta(minutes=4),
        )
        session = FakeSession(records=[due, future, fresh_locked, expired_locked])

        claimed = await claim_available_events(
            session,
            worker_id="worker-new",
            now=now,
            limit=10,
            lock_timeout=timedelta(minutes=5),
        )

        self.assertEqual([event.event_id for event in claimed], ["expired-locked", "due"])
        self.assertEqual(expired_locked.status, "locked")
        self.assertEqual(expired_locked.locked_by, "worker-new")
        self.assertEqual(expired_locked.attempts, 3)
        self.assertEqual(due.locked_by, "worker-new")
        self.assertEqual(due.attempts, 1)
        self.assertEqual(future.status, "pending")
        self.assertEqual(fresh_locked.locked_by, "worker-old")

    async def test_publish_outbox_batch_marks_successful_events_published(self):
        from ai.outbox.publisher import publish_outbox_batch

        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={"ok": True},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
            updated_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])
        published = []

        async def publisher(row):
            published.append(row.event_id)

        result = await publish_outbox_batch(
            sessionmaker=FakeSessionFactory(session),
            publisher=publisher,
            worker_id="worker-1",
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.published, 1)
        self.assertEqual(published, ["event-1"])
        self.assertEqual(event.status, "published")

    async def test_publish_outbox_batch_retries_failed_events(self):
        from ai.outbox.publisher import publish_outbox_batch

        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
            updated_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])

        async def publisher(_row):
            raise RuntimeError("temporary")

        result = await publish_outbox_batch(
            sessionmaker=FakeSessionFactory(session),
            publisher=publisher,
            worker_id="worker-1",
            max_attempts=3,
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.retried, 1)
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.last_error, "temporary")

    async def test_publish_outbox_batch_moves_exhausted_events_to_dlq(self):
        from ai.outbox.publisher import publish_outbox_batch

        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=2,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
            updated_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])

        async def publisher(_row):
            raise RuntimeError("poison")

        result = await publish_outbox_batch(
            sessionmaker=FakeSessionFactory(session),
            publisher=publisher,
            worker_id="worker-1",
            max_attempts=3,
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.dead_lettered, 1)
        self.assertEqual(event.status, "dead")
        self.assertEqual(event.last_error, "poison")

    async def test_publish_outbox_batch_uses_handler_registry(self):
        from ai.outbox.handlers import OutboxHandlerRegistry
        from ai.outbox.publisher import publish_outbox_batch

        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])
        handled = []
        registry = OutboxHandlerRegistry()

        async def handler(row):
            handled.append(row.event_id)

        registry.register("turn_completed", handler)

        result = await publish_outbox_batch(
            sessionmaker=FakeSessionFactory(session),
            handler_registry=registry,
            worker_id="worker-1",
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.published, 1)
        self.assertEqual(handled, ["event-1"])
        self.assertEqual(event.status, "published")

    async def test_unregistered_handler_retries_with_specific_error(self):
        from ai.outbox.handlers import OutboxHandlerRegistry
        from ai.outbox.publisher import publish_outbox_batch

        event = OutboxEvent(
            event_id="event-1",
            event_type="unknown_event",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])

        result = await publish_outbox_batch(
            sessionmaker=FakeSessionFactory(session),
            handler_registry=OutboxHandlerRegistry(),
            worker_id="worker-1",
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.retried, 1)
        self.assertIn("no outbox handler registered", event.last_error)


class Phase6OutboxAdminQueryWorkerTest(unittest.IsolatedAsyncioTestCase):
    async def test_dead_event_can_be_requeued_and_abandoned(self):
        from ai.outbox.admin import abandon_dead_event, requeue_dead_event

        now = datetime(2026, 5, 26, 12, 0, 0)
        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={"request_id": "request-1"},
            status="dead",
            attempts=3,
            locked_at=now - timedelta(minutes=1),
            locked_by="worker-old",
            last_error="poison",
        )
        session = FakeSession(records=[event])

        requeued = await requeue_dead_event(session, "event-1", reset_attempts=True, now=now)

        self.assertIs(requeued, event)
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.attempts, 0)
        self.assertIsNone(event.locked_by)
        self.assertIsNone(event.locked_at)
        self.assertEqual(event.next_attempt_at, now)
        self.assertEqual(event.last_error, "poison")

        event.status = "dead"
        abandoned = await abandon_dead_event(session, "event-1", "operator reviewed", now=now)

        self.assertIs(abandoned, event)
        self.assertEqual(event.status, "abandoned")
        self.assertIn("operator reviewed", event.last_error)

    async def test_outbox_queries_filter_and_summarize_events(self):
        from ai.outbox.queries import OutboxQuery, get_outbox_event_detail, list_outbox_events, summarize_outbox

        records = [
            OutboxEvent(
                event_id="event-1",
                event_type="turn_completed",
                aggregate_type="session",
                aggregate_id="session-1",
                payload={"request_id": "request-1"},
                status="pending",
                attempts=0,
                created_at=datetime(2026, 5, 26, 12, 0, 0),
            ),
            OutboxEvent(
                event_id="event-2",
                event_type="run_failed",
                aggregate_type="run",
                aggregate_id="run-1",
                payload={"run_id": "run-1"},
                status="dead",
                attempts=3,
                last_error="poison",
                created_at=datetime(2026, 5, 26, 12, 5, 0),
            ),
        ]
        session = FakeSession(records=records)

        dead = await list_outbox_events(session, OutboxQuery(status="dead"))
        summary = await summarize_outbox(session)
        detail = await get_outbox_event_detail(session, "event-2")

        self.assertEqual([event.event_id for event in dead], ["event-2"])
        self.assertEqual(summary["pending"], 1)
        self.assertEqual(summary["dead"], 1)
        self.assertEqual(detail["payload"], {"run_id": "run-1"})
        self.assertEqual(detail["last_error"], "poison")

    async def test_run_outbox_worker_once_returns_publish_counts(self):
        from ai.outbox.handlers import OutboxHandlerRegistry
        from ai.outbox.worker import run_outbox_worker_once

        event = OutboxEvent(
            event_id="event-1",
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 5, 26, 12, 0, 0),
            created_at=datetime(2026, 5, 26, 12, 0, 0),
        )
        session = FakeSession(records=[event])
        registry = OutboxHandlerRegistry()

        async def handler(_row):
            return None

        registry.register("turn_completed", handler)

        result = await run_outbox_worker_once(
            sessionmaker=FakeSessionFactory(session),
            handler_registry=registry,
            worker_id="worker-1",
            batch_size=10,
            now=datetime(2026, 5, 26, 12, 1, 0),
        )

        self.assertEqual(result.claimed, 1)
        self.assertEqual(result.published, 1)
        self.assertEqual(event.status, "published")


class Phase6CacheTest(unittest.TestCase):
    def test_request_result_cache_hits_misses_and_expires(self):
        from ai.cache.idempotency_cache import RequestResultCache

        now = datetime(2026, 5, 26, 12, 0, 0)
        cache = RequestResultCache(default_ttl=timedelta(seconds=10))

        self.assertIsNone(cache.get("request-1", now=now))
        cache.set("request-1", {"answer": "cached"}, now=now)

        self.assertEqual(cache.get("request-1", now=now + timedelta(seconds=5)), {"answer": "cached"})
        self.assertIsNone(cache.get("request-1", now=now + timedelta(seconds=11)))
        self.assertEqual(cache.stats()["hits"], 1)
        self.assertEqual(cache.stats()["misses"], 2)


class Phase6DebugSnapshotTest(unittest.IsolatedAsyncioTestCase):
    async def test_enhanced_debug_snapshot_includes_outbox_cache_and_provider_trace(self):
        from ai.observability.debug_snapshot import build_enhanced_debug_snapshot

        repository = type(
            "Repository",
            (),
            {
                "run": type("Run", (), {"checkpoint_payload": {"step": "done"}})(),
                "events": [type("Event", (), {"event_type": "answer", "payload": {"answer": "ok"}})()],
                "artifacts": [type("Artifact", (), {"artifact_type": "response_refs", "payload": {}})()],
            },
        )()

        async def list_events(_run_id):
            return list(repository.events)

        async def list_artifacts(_run_id):
            return list(repository.artifacts)

        repository.list_events = list_events
        repository.list_artifacts = list_artifacts
        outbox_events = [
            OutboxEvent(
                event_id="event-1",
                event_type="turn_completed",
                aggregate_type="session",
                aggregate_id="session-1",
                payload={},
                status="dead",
                attempts=3,
            )
        ]

        snapshot = await build_enhanced_debug_snapshot(
            repository=repository,
            run_id="run-1",
            outbox_events=outbox_events,
            cache_stats={"hits": 2, "misses": 1},
            provider_trace=[{"provider": "openai", "model": "planner"}],
        )

        self.assertEqual(snapshot["run_id"], "run-1")
        self.assertEqual(snapshot["outbox"][0]["status"], "dead")
        self.assertEqual(snapshot["outbox"][0]["last_error"], None)
        self.assertIn("worker", snapshot)
        self.assertEqual(snapshot["cache"]["hits"], 2)
        self.assertEqual(snapshot["provider_trace"][0]["provider"], "openai")


if __name__ == "__main__":
    unittest.main()
