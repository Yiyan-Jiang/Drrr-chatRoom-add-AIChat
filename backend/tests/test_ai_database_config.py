import os
import unittest
from unittest.mock import patch

from ai.database import get_ai_database_url


class AIDatabaseConfigTest(unittest.TestCase):
    def test_get_ai_database_url_requires_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AI_DATABASE_URL is not set"):
                get_ai_database_url()

    def test_get_ai_database_url_reads_ai_database_url(self):
        with patch.dict(
            os.environ,
            {"AI_DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/ai_chat"},
            clear=True,
        ):
            self.assertEqual(
                get_ai_database_url(),
                "postgresql+asyncpg://user:pass@localhost:5432/ai_chat",
            )

    def test_ai_migration_error_mentions_ai_alembic_command_and_head(self):
        from ai.database import (
            AI_ALEMBIC_VERSION_TABLE,
            assert_ai_migration_revision_is_head,
            build_ai_migration_revision_mismatch_error,
            build_missing_ai_migration_error,
            get_ai_alembic_head_revision,
        )

        missing = build_missing_ai_migration_error()

        self.assertIn(AI_ALEMBIC_VERSION_TABLE, missing)
        self.assertIn("alembic -c ai/alembic.ini upgrade head", missing)
        self.assertIn("alembic -c ai/alembic.ini stamp head", missing)
        self.assertIn("ai_chat_history already exists", missing)
        self.assertNotIn("normal_system/alembic.ini", missing)
        self.assertEqual(get_ai_alembic_head_revision(), "0001_create_ai_chat_history")

        mismatch = build_ai_migration_revision_mismatch_error("old_revision", "head_revision")
        self.assertIn("old_revision", mismatch)
        self.assertIn("head_revision", mismatch)
        self.assertIn("alembic -c ai/alembic.ini upgrade head", mismatch)

        assert_ai_migration_revision_is_head(
            current_revision="head_revision",
            head_revision="head_revision",
        )
        with self.assertRaisesRegex(RuntimeError, "alembic -c ai/alembic.ini upgrade head"):
            assert_ai_migration_revision_is_head(
                current_revision="old_revision",
                head_revision="head_revision",
            )


if __name__ == "__main__":
    unittest.main()
