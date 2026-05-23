import unittest
from datetime import datetime

from ai.models.chat_history import AIChatHistory
from ai.repositories.chat_history_repository import (
    create_ai_chat_history,
    delete_all_ai_chat_history,
    get_user_ai_chat_history,
)


class FakeScalarResult:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records


class FakeExecuteResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return FakeScalarResult(self._records)


class FakeSession:
    def __init__(self, records=None):
        self.records = records or []
        self.added = []
        self.deleted = []
        self.commits = 0
        self.refreshed = []

    def add(self, record):
        self.added.append(record)
        self.records.append(record)

    async def commit(self):
        self.commits += 1

    async def refresh(self, record):
        self.refreshed.append(record)

    async def execute(self, _statement):
        return FakeExecuteResult(list(self.records))

    async def delete(self, record):
        self.deleted.append(record)
        self.records.remove(record)


class AIChatHistoryRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_ai_chat_history_sets_minimal_fields(self):
        session = FakeSession()

        record = await create_ai_chat_history(
            session,
            user_id=7,
            role="user",
            content="hello",
            character="rin",
        )

        self.assertIsInstance(record, AIChatHistory)
        self.assertEqual(record.__tablename__, "ai_chat_history")
        self.assertEqual(record.user_id, 7)
        self.assertEqual(record.role, "user")
        self.assertEqual(record.content, "hello")
        self.assertEqual(record.character, "rin")
        self.assertIsInstance(record.created_at, datetime)
        self.assertEqual(session.commits, 1)
        self.assertEqual(session.refreshed, [record])

    async def test_get_user_ai_chat_history_returns_oldest_first(self):
        first = AIChatHistory(user_id=7, character="sakura", role="user", content="first")
        second = AIChatHistory(user_id=7, character="sakura", role="assistant", content="second")
        session = FakeSession(records=[second, first])

        records = await get_user_ai_chat_history(
            session,
            user_id=7,
            limit=8,
            character="sakura",
        )

        self.assertEqual(records, [first, second])

    async def test_delete_all_ai_chat_history_deletes_selected_records(self):
        first = AIChatHistory(user_id=7, character="sakura", role="user", content="first")
        second = AIChatHistory(user_id=7, character="sakura", role="assistant", content="second")
        session = FakeSession(records=[first, second])

        count = await delete_all_ai_chat_history(
            session,
            user_id=7,
            character="sakura",
        )

        self.assertEqual(count, 2)
        self.assertEqual(session.deleted, [first, second])
        self.assertEqual(session.records, [])
        self.assertEqual(session.commits, 1)


if __name__ == "__main__":
    unittest.main()
