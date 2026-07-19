import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn
from ai.models.outbox_event import OutboxEvent


class FakeScalarResult:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records


class FakeExecuteResult:
    def __init__(self, records, rowcount=0):
        self._records = records
        self.rowcount = rowcount

    def scalars(self):
        return FakeScalarResult(self._records)

    def scalar_one_or_none(self):
        return self._records[0] if self._records else None


class FakeSession:
    def __init__(self, records=None):
        self.records = records or []
        self.added = []
        self.flushes = 0
        self.commits = 0

    def add(self, record):
        self.added.append(record)
        self.records.append(record)

    async def flush(self):
        self.flushes += 1

    async def commit(self):
        self.commits += 1

    async def execute(self, statement):
        text = str(statement)
        if text.startswith("DELETE"):
            before = len(self.records)
            if "agent_memories" in text:
                self.records = [
                    record
                    for record in self.records
                    if record.__class__.__name__ != "AgentMemory"
                ]
            elif "outbox_events" in text:
                self.records = [
                    record
                    for record in self.records
                    if not (
                        isinstance(record, OutboxEvent)
                        and record.event_type == "ai_memory_extract_requested"
                    )
                ]
            return FakeExecuteResult([], rowcount=before - len(self.records))
        return FakeExecuteResult(list(self.records))


class FakeSessionFactory:
    def __init__(self, session):
        self.session = session

    def __call__(self):
        return self

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class LongTermMemoryModelMigrationTest(unittest.TestCase):
    def test_agent_memory_model_uses_expected_table(self):
        from ai.models.agent_memory import AgentMemory

        self.assertEqual(AgentMemory.__tablename__, "agent_memories")
        self.assertIn("memory_id", AgentMemory.__table__.c)
        self.assertIn("user_id", AgentMemory.__table__.c)
        self.assertIn("character", AgentMemory.__table__.c)
        self.assertIn("source_turn_id", AgentMemory.__table__.c)

    def test_agent_memory_migration_is_after_current_head(self):
        root = Path(__file__).resolve().parents[1]
        migration = root / "ai" / "alembic" / "versions" / "0006_create_agent_memories.py"

        text = migration.read_text(encoding="utf-8")

        self.assertIn('revision: str = "0006_create_agent_memories"', text)
        self.assertIn('down_revision: Union[str, None] = "0005_harness_skill_state"', text)
        self.assertIn('"agent_memories"', text)
        self.assertIn('"ix_agent_memories_user_character_status"', text)


class LongTermMemoryRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_extract_and_store_user_preference_memory(self):
        from ai.memory.worker import extract_memory_for_turn
        from ai.memory.repositories import create_agent_memory

        now = datetime(2026, 7, 19, 12, 0, 0)
        turn = AgentTurn(
            id=11,
            session_id="session-1",
            user_id=7,
            sequence_no=3,
            role="user",
            content="以后回答都用中文，先给方案，确认后再改代码",
            character="sakura",
            created_at=now,
        )
        extracted = extract_memory_for_turn(user_id=7, session_id="session-1", turn=turn)

        self.assertEqual(len(extracted), 1)
        self.assertEqual(extracted[0].memory_type, "instruction")

        session = FakeSession()
        record = await create_agent_memory(
            session,
            item=extracted[0],
            character="sakura",
            source_turn_id=turn.id,
            now=now,
        )

        self.assertEqual(record.user_id, 7)
        self.assertEqual(record.character, "sakura")
        self.assertEqual(record.status, "active")
        self.assertEqual(record.source_turn_id, 11)
        self.assertIn("先给方案", record.content)
        self.assertEqual(session.flushes, 1)

    async def test_clear_memory_deletes_memories_and_pending_extract_events(self):
        from ai.memory.repositories import clear_user_agent_memory
        from ai.models.agent_memory import AgentMemory

        memory = AgentMemory(
            memory_id="memory-1",
            user_id=7,
            character="sakura",
            session_id="session-1",
            memory_type="instruction",
            content="先给方案",
            importance=5,
            confidence=0.9,
            status="active",
        )
        pending = OutboxEvent(
            event_id="event-1",
            event_type="ai_memory_extract_requested",
            aggregate_type="session",
            aggregate_id="session-1",
            payload={"user_id": 7, "character": "sakura"},
            status="pending",
            attempts=0,
            next_attempt_at=datetime(2026, 7, 19, 12, 0, 0),
        )
        session = FakeSession(records=[memory, pending])

        cleared_memories, cleared_events = await clear_user_agent_memory(
            session,
            user_id=7,
            character="sakura",
        )

        self.assertEqual(cleared_memories, 1)
        self.assertEqual(cleared_events, 1)

    async def test_create_agent_memory_reuses_existing_source_turn_memory(self):
        from ai.memory.models import AgentMemoryItem
        from ai.memory.repositories import create_agent_memory
        from ai.models.agent_memory import AgentMemory

        existing = AgentMemory(
            memory_id="memory-1",
            user_id=7,
            character="sakura",
            session_id="session-1",
            source_turn_id=11,
            source_sequence_no=3,
            memory_type="instruction",
            content="旧内容",
            importance=3,
            confidence=0.7,
            status="active",
        )
        session = FakeSession(records=[existing])

        record = await create_agent_memory(
            session,
            item=AgentMemoryItem(
                user_id=7,
                session_id="session-1",
                memory_type="instruction",
                content="新内容",
                source_sequence_no=3,
                importance=5,
                confidence=0.9,
            ),
            character="sakura",
            source_turn_id=11,
            now=datetime(2026, 7, 19, 12, 0, 0),
        )

        self.assertIs(record, existing)
        self.assertEqual(record.content, "新内容")
        self.assertEqual(record.importance, 5)
        self.assertEqual(session.added, [])


class LongTermMemoryContextTest(unittest.TestCase):
    def test_compile_context_includes_long_term_memories(self):
        from ai.harness.context import compile_context
        from ai.models.agent_memory import AgentMemory

        workspace = SimpleNamespace(
            command=SimpleNamespace(message="你还记得我的偏好吗？", character="sakura"),
            session=SimpleNamespace(session_id="session-1", user_id=7),
            recent_turns=[],
            long_term_memories=[
                AgentMemory(
                    memory_id="memory-1",
                    user_id=7,
                    character="sakura",
                    memory_type="instruction",
                    content="用户希望先给方案，确认后再改代码",
                    importance=5,
                    confidence=0.9,
                    status="active",
                )
            ],
        )

        context = compile_context(
            workspace=workspace,
            run=SimpleNamespace(run_id="run-1", checkpoint_payload={}),
            events=[],
            artifacts=[],
        )

        sections = [item.section for item in context.ledger]
        content = "\n".join(message["content"] for message in context.messages)

        self.assertIn("long_term_memories", sections)
        self.assertIn("先给方案", content)


class LongTermMemoryPersistenceTest(unittest.IsolatedAsyncioTestCase):
    async def test_background_enqueue_creates_memory_extract_event_from_saved_turns(self):
        from ai.memory.background import enqueue_memory_extraction_for_request

        user_turn = AgentTurn(
            id=11,
            session_id="session-1",
            user_id=7,
            sequence_no=1,
            role="user",
            content="以后回答都用中文",
            request_id="request-1",
            character="sakura",
        )
        assistant_turn = AgentTurn(
            id=12,
            session_id="session-1",
            user_id=7,
            sequence_no=2,
            role="assistant",
            content="好的",
            request_id="request-1",
            character="sakura",
        )
        db = FakeSession(records=[user_turn, assistant_turn])

        await enqueue_memory_extraction_for_request(
            request_id="request-1",
            user_id=7,
            session_id="session-1",
            character="sakura",
            sessionmaker=FakeSessionFactory(db),
        )

        memory_events = [
            record
            for record in db.added
            if isinstance(record, OutboxEvent)
            and record.event_type == "ai_memory_extract_requested"
        ]
        self.assertEqual(len(memory_events), 1)
        self.assertEqual(memory_events[0].payload["user_turn_id"], 11)
        self.assertEqual(memory_events[0].payload["assistant_turn_id"], 12)
        self.assertEqual(db.commits, 1)

    async def test_persist_success_does_not_enqueue_memory_extraction_before_response(self):
        from ai.orchestrator.persistence import persist_success
        from ai.orchestrator.schemas import AITurnCommand, AITurnResult, RunResult
        from ai.models.agent_turn_audit import AgentTurnAudit

        session_record = AgentSession(
            session_id="session-1",
            user_id=7,
            status="active",
            last_sequence_no=0,
        )
        audit = AgentTurnAudit(
            request_id="request-1",
            user_id=7,
            status="running",
            stage="runtime_running",
        )
        db = FakeSession(records=[session_record, audit])

        await persist_success(
            db=db,
            command=AITurnCommand(
                request_id="request-1",
                session_id="session-1",
                user_id=7,
                message="以后回答都用中文",
                character="sakura",
            ),
            session=session_record,
            run_result=RunResult(answer="好的"),
            response=AITurnResult(
                request_id="request-1",
                session_id="session-1",
                answer="好的",
                status="completed",
            ),
            now=datetime(2026, 7, 19, 12, 0, 0),
        )

        memory_events = [
            record
            for record in db.added
            if isinstance(record, OutboxEvent)
            and record.event_type == "ai_memory_extract_requested"
        ]
        self.assertEqual(memory_events, [])


if __name__ == "__main__":
    unittest.main()
