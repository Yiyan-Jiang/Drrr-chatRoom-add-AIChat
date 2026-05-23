import os
import unittest
from unittest.mock import patch


class Phase5DatabaseContractTest(unittest.TestCase):
    def test_sqlalchemy_metadata_keeps_normal_and_ai_tables_separate(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
                "AI_DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/ai_chat",
            },
        ):
            import normal_system.models  # noqa: F401
            import ai.models.chat_history  # noqa: F401
            from ai.database import AIBase
            from ai.models.chat_history import AIChatHistory
            from common.normal_database import Login

        self.assertEqual(
            set(Login.metadata.tables),
            {"chatRoom_user", "chatRoom_room", "chatRoom_message"},
        )
        self.assertEqual(set(AIBase.metadata.tables), {"ai_chat_history"})
        self.assertEqual(set(AIChatHistory.__table__.foreign_keys), set())

    def test_migration_files_keep_database_boundaries(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        normal_migrations = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (root / "normal_system" / "alembic" / "versions").glob("*.py")
        )
        ai_migrations = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (root / "ai" / "alembic" / "versions").glob("*.py")
        )

        self.assertIn("chatRoom_user", normal_migrations)
        self.assertIn("chatRoom_room", normal_migrations)
        self.assertIn("chatRoom_message", normal_migrations)
        self.assertNotIn("ai_chat_history", normal_migrations)

        self.assertIn("ai_chat_history", ai_migrations)
        self.assertNotIn("chatRoom_user", ai_migrations)
        self.assertNotIn("chatRoom_room", ai_migrations)
        self.assertNotIn("chatRoom_message", ai_migrations)
        self.assertNotIn("ForeignKeyConstraint", ai_migrations)


if __name__ == "__main__":
    unittest.main()
