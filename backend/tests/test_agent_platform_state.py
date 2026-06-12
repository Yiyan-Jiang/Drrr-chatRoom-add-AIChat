import unittest
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError


class FakeScalarResult:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records


class FakeExecuteResult:
    def __init__(self, records):
        self._records = records

    def scalar_one_or_none(self):
        return self._records[0] if self._records else None

    def scalars(self):
        return FakeScalarResult(self._records)


class FakeSession:
    def __init__(self, records=None, commit_error=None):
        self.records = records or []
        self.added = []
        self.statements = []
        self.commits = 0
        self.rollbacks = 0
        self.flushes = 0
        self.refreshed = []
        self.commit_error = commit_error

    def add(self, record):
        self.added.append(record)
        self.records.append(record)

    async def execute(self, _statement):
        self.statements.append(_statement)
        return FakeExecuteResult(list(self.records))

    async def commit(self):
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    async def rollback(self):
        self.rollbacks += 1

    async def flush(self):
        self.flushes += 1

    async def refresh(self, record):
        self.refreshed.append(record)


class AgentPlatformModelContractTest(unittest.TestCase):
    def test_phase2_models_use_expected_table_names_and_nullable_fields(self):
        from ai.models.agent_session import AgentSession
        from ai.models.agent_turn import AgentTurn
        from ai.models.agent_turn_audit import AgentTurnAudit
        from ai.models.harness_run import HarnessRun

        self.assertEqual(AgentSession.__tablename__, "agent_sessions")
        self.assertTrue(AgentSession.__table__.c.title.nullable)
        self.assertTrue(AgentSession.__table__.c.extra_payload.nullable)

        self.assertEqual(AgentTurn.__tablename__, "agent_turns")
        self.assertTrue(AgentTurn.__table__.c.request_id.nullable)
        self.assertTrue(AgentTurn.__table__.c.character.nullable)
        self.assertTrue(AgentTurn.__table__.c.extra_payload.nullable)

        self.assertEqual(AgentTurnAudit.__tablename__, "agent_turn_audit")
        self.assertIn("request_id", AgentTurnAudit.__table__.c)
        self.assertNotIn("requests_id", AgentTurnAudit.__table__.c)
        self.assertEqual(str(AgentTurnAudit.__table__.c.session_id.type), "VARCHAR(64)")
        self.assertTrue(AgentTurnAudit.__table__.c.completed_at.nullable)

        self.assertEqual(HarnessRun.__tablename__, "harness_runs")
        self.assertIn("skill_state_payload", HarnessRun.__table__.c)
        self.assertTrue(HarnessRun.__table__.c.skill_state_payload.nullable)

    def test_repair_migration_adds_missing_harness_run_skill_state_column(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        migration = (
            root
            / "ai"
            / "alembic"
            / "versions"
            / "0005_harness_skill_state.py"
        )

        text = migration.read_text(encoding="utf-8")

        self.assertIn('revision: str = "0005_harness_skill_state"', text)
        self.assertIn('down_revision: Union[str, None] = "0004_create_governance_baseline"', text)
        self.assertIn('"harness_runs"', text)
        self.assertIn('"skill_state_payload"', text)


class AgentAuditRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_reserve_request_inserts_pending_audit_and_commits_reservation(self):
        from ai.repositories.agent_audit_repository import reserve_request

        session = FakeSession()
        now = datetime(2026, 5, 25, 12, 0, 0)

        reservation = await reserve_request(
            session,
            request_id="req-1",
            user_id=7,
            session_id="s-1",
            now=now,
        )

        self.assertEqual(reservation.kind, "accepted")
        self.assertEqual(reservation.audit.request_id, "req-1")
        self.assertEqual(reservation.audit.status, "pending")
        self.assertEqual(reservation.audit.stage, "reserved")
        self.assertEqual(reservation.audit.created_at, now)
        self.assertEqual(session.commits, 1)
        self.assertEqual(session.refreshed, [reservation.audit])

    async def test_reserve_request_resolves_existing_audit_after_unique_conflict(self):
        from ai.models.agent_turn_audit import AgentTurnAudit
        from ai.repositories.agent_audit_repository import reserve_request

        existing = AgentTurnAudit(
            request_id="req-1",
            user_id=7,
            session_id="s-1",
            status="completed",
            response_payload={"answer": "cached"},
        )
        session = FakeSession(
            records=[existing],
            commit_error=IntegrityError("insert", {}, Exception("duplicate")),
        )

        reservation = await reserve_request(session, "req-1", user_id=7, session_id="s-1")

        self.assertEqual(reservation.kind, "completed")
        self.assertEqual(reservation.response_payload, {"answer": "cached"})
        self.assertEqual(session.rollbacks, 1)

    async def test_mark_audit_completed_flushes_without_committing(self):
        from ai.models.agent_turn_audit import AgentTurnAudit
        from ai.repositories.agent_audit_repository import mark_audit_completed

        audit = AgentTurnAudit(
            request_id="req-1",
            user_id=7,
            status="running",
            stage="model_running",
        )
        session = FakeSession(records=[audit])
        now = datetime(2026, 5, 25, 12, 30, 0)

        updated = await mark_audit_completed(
            session,
            request_id="req-1",
            response_payload={"answer": "ok"},
            now=now,
        )

        self.assertIs(updated, audit)
        self.assertEqual(audit.status, "completed")
        self.assertEqual(audit.stage, "completed")
        self.assertEqual(audit.response_payload, {"answer": "ok"})
        self.assertEqual(audit.completed_at, now)
        self.assertEqual(session.flushes, 1)
        self.assertEqual(session.commits, 0)


class AgentSessionTurnRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_session_flushes_without_committing(self):
        from ai.repositories.agent_session_repository import create_agent_session

        session = FakeSession()
        now = datetime(2026, 5, 25, 13, 0, 0)

        agent_session = await create_agent_session(
            session,
            user_id=7,
            session_id="s-1",
            title="demo",
            now=now,
        )

        self.assertEqual(agent_session.session_id, "s-1")
        self.assertEqual(agent_session.user_id, 7)
        self.assertEqual(agent_session.status, "active")
        self.assertEqual(agent_session.last_sequence_no, 0)
        self.assertEqual(agent_session.created_at, now)
        self.assertEqual(session.flushes, 1)
        self.assertEqual(session.commits, 0)

    async def test_append_turn_pair_increments_session_sequence(self):
        from ai.models.agent_session import AgentSession
        from ai.repositories.agent_turn_repository import append_turn_pair

        agent_session = AgentSession(session_id="s-1", user_id=7, last_sequence_no=0)
        session = FakeSession(records=[agent_session])
        now = datetime(2026, 5, 25, 13, 10, 0)

        user_turn, assistant_turn = await append_turn_pair(
            session,
            session_id="s-1",
            user_id=7,
            request_id="req-1",
            user_content="hello",
            assistant_content="hi",
            character="rin",
            now=now,
        )

        self.assertEqual(user_turn.sequence_no, 1)
        self.assertEqual(user_turn.role, "user")
        self.assertEqual(assistant_turn.sequence_no, 2)
        self.assertEqual(assistant_turn.role, "assistant")
        self.assertEqual(agent_session.last_sequence_no, 2)
        self.assertEqual(agent_session.updated_at, now)
        self.assertEqual(session.flushes, 1)
        self.assertEqual(session.commits, 0)


class AgentArtifactRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_list_artifacts_builds_query_for_store_extension_filters(self):
        from ai.repositories.artifact_repository import list_artifacts

        session = FakeSession()

        await list_artifacts(
            session,
            run_id="run-1",
            session_id="s-1",
            request_id="req-1",
            user_id=7,
        )

        statement = str(session.statements[-1])
        self.assertIn("agent_artifacts.run_id", statement)
        self.assertIn("agent_artifacts.session_id", statement)
        self.assertIn("agent_artifacts.request_id", statement)
        self.assertIn("agent_artifacts.user_id", statement)


class OutboxRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_outbox_event_starts_pending_and_flushes(self):
        from ai.repositories.outbox_repository import create_outbox_event

        session = FakeSession()
        now = datetime(2026, 5, 25, 14, 0, 0)

        event = await create_outbox_event(
            session,
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id="s-1",
            payload={"request_id": "req-1"},
            now=now,
        )

        self.assertEqual(event.status, "pending")
        self.assertEqual(event.attempts, 0)
        self.assertEqual(event.next_attempt_at, now)
        self.assertEqual(session.flushes, 1)
        self.assertEqual(session.commits, 0)

    async def test_mark_event_retry_uses_attempt_count_for_backoff(self):
        from ai.models.outbox_event import OutboxEvent
        from ai.repositories.outbox_repository import mark_event_retry

        now = datetime(2026, 5, 25, 14, 5, 0)
        event = OutboxEvent(event_id="event-1", attempts=3, status="locked")
        session = FakeSession(records=[event])

        updated = await mark_event_retry(
            session,
            event_id="event-1",
            error_message="temporary",
            now=now,
        )

        self.assertIs(updated, event)
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.last_error, "temporary")
        self.assertEqual(event.next_attempt_at, now + timedelta(seconds=8))
        self.assertEqual(session.commits, 1)


if __name__ == "__main__":
    unittest.main()
