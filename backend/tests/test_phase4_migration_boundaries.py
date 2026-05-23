from pathlib import Path
import unittest


class Phase4MigrationBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_root_schema_migrations_module_is_removed(self):
        self.assertFalse((self.root / "schema_migrations.py").exists())

    def test_startup_database_modules_verify_alembic_heads(self):
        normal_database = (self.root / "common" / "normal_database.py").read_text(encoding="utf-8")
        ai_database = (self.root / "ai" / "database.py").read_text(encoding="utf-8")

        self.assertIn("get_normal_alembic_head_revision", normal_database)
        self.assertIn("build_normal_migration_revision_mismatch_error", normal_database)
        self.assertIn("get_ai_alembic_head_revision", ai_database)
        self.assertIn("build_ai_migration_revision_mismatch_error", ai_database)
        self.assertIn("SELECT version_num", normal_database)
        self.assertIn("SELECT version_num", ai_database)


if __name__ == "__main__":
    unittest.main()
