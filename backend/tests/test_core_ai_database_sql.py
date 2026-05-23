from pathlib import Path
import unittest


class CoreAIDatabaseSQLTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.sql_path = self.root / "core" / "init_ai_database.sql"

    def test_core_has_postgresql_ai_database_init_script(self):
        self.assertTrue(self.sql_path.exists())

        content = self.sql_path.read_text(encoding="utf-8")

        self.assertIn("CREATE DATABASE ai_chat", content)
        self.assertIn("CREATE ROLE ai_user", content)
        self.assertIn(r"\connect ai_chat", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS ai_chat_history", content)
        self.assertIn("ix_ai_chat_history_user_id", content)
        self.assertIn("ix_ai_chat_history_character", content)
        self.assertIn("INSERT INTO alembic_version", content)
        self.assertIn("0001_create_ai_chat_history", content)
        self.assertNotIn("USE ai_chat", content)

    def test_core_ai_table_columns_match_ai_migration(self):
        content = self.sql_path.read_text(encoding="utf-8")

        self.assertIn("id SERIAL PRIMARY KEY", content)
        self.assertIn("user_id INTEGER NOT NULL", content)
        self.assertIn("character VARCHAR(20) NOT NULL DEFAULT 'sakura'", content)
        self.assertIn("role VARCHAR(20) NOT NULL", content)
        self.assertIn("content TEXT NOT NULL", content)
        self.assertIn("created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL", content)


if __name__ == "__main__":
    unittest.main()
