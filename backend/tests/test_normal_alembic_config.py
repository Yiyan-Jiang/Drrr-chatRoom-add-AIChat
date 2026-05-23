from pathlib import Path
import unittest


class NormalAlembicConfigTest(unittest.TestCase):
    def test_normal_system_has_separate_alembic_environment(self):
        root = Path(__file__).resolve().parents[1]

        self.assertTrue((root / "normal_system" / "alembic.ini").exists())
        self.assertTrue((root / "normal_system" / "alembic" / "env.py").exists())
        self.assertTrue((root / "normal_system" / "alembic" / "script.py.mako").exists())
        self.assertTrue((root / "normal_system" / "alembic" / "versions").is_dir())

    def test_normal_initial_migration_keeps_existing_table_names(self):
        root = Path(__file__).resolve().parents[1]
        migration = root / "normal_system" / "alembic" / "versions" / "0001_normal_initial_schema.py"
        content = migration.read_text(encoding="utf-8")

        self.assertIn('"chatRoom_user"', content)
        self.assertIn('"chatRoom_room"', content)
        self.assertIn('"chatRoom_message"', content)
        self.assertNotIn("chatRoom_ai_chat_history", content)
        self.assertNotIn("ai_chat_history", content)


if __name__ == "__main__":
    unittest.main()
