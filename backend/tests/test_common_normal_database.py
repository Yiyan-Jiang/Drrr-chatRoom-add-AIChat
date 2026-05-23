from pathlib import Path
import unittest
from unittest.mock import patch


class CommonNormalDatabaseTest(unittest.TestCase):
    def test_missing_normal_migration_error_mentions_normal_alembic_command(self):
        with patch.dict(
            "os.environ",
            {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms"},
        ):
            from common.normal_database import (
                NORMAL_ALEMBIC_VERSION_TABLE,
                build_missing_normal_migration_error,
                build_normal_migration_revision_mismatch_error,
                get_normal_alembic_head_revision,
            )

        message = build_missing_normal_migration_error()

        self.assertIn(NORMAL_ALEMBIC_VERSION_TABLE, message)
        self.assertIn("alembic -c normal_system/alembic.ini upgrade head", message)
        self.assertNotIn("ai/alembic.ini", message)

        self.assertEqual(get_normal_alembic_head_revision(), "0001_normal_initial_schema")
        mismatch = build_normal_migration_revision_mismatch_error("old_revision", "head_revision")
        self.assertIn("old_revision", mismatch)
        self.assertIn("head_revision", mismatch)
        self.assertIn("alembic -c normal_system/alembic.ini upgrade head", mismatch)

    def test_normal_revision_assertion_rejects_non_head_revision(self):
        from common.normal_database import assert_normal_migration_revision_is_head

        assert_normal_migration_revision_is_head(
            current_revision="head_revision",
            head_revision="head_revision",
        )

        with self.assertRaisesRegex(RuntimeError, "alembic -c normal_system/alembic.ini upgrade head"):
            assert_normal_migration_revision_is_head(
                current_revision="old_revision",
                head_revision="head_revision",
            )

    def test_backend_modules_import_common_normal_database(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "normal_system" / "bootstrap.py",
            root / "normal_system" / "routers" / "auth.py",
            root / "normal_system" / "routers" / "message.py",
            root / "normal_system" / "routers" / "room.py",
            root / "normal_system" / "routers" / "socket.py",
            root / "normal_system" / "routers" / "user.py",
            root / "normal_system" / "alembic" / "env.py",
        ]

        joined = "\n".join(path.read_text(encoding="utf-8") for path in files)

        self.assertIn("common.normal_database", joined)
        self.assertNotIn("from database import", joined)


if __name__ == "__main__":
    unittest.main()
