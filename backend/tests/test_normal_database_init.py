import unittest
from unittest.mock import patch


class NormalDatabaseInitTest(unittest.TestCase):
    def test_missing_normal_migration_error_mentions_alembic_command(self):
        with patch.dict(
            "os.environ",
            {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms"},
        ):
            from common.normal_database import (
                NORMAL_ALEMBIC_VERSION_TABLE,
                build_missing_normal_migration_error,
            )

        message = build_missing_normal_migration_error()

        self.assertIn(NORMAL_ALEMBIC_VERSION_TABLE, message)
        self.assertIn("alembic -c normal_system/alembic.ini upgrade head", message)
        self.assertIn("alembic -c normal_system/alembic.ini stamp head", message)
        self.assertIn("legacy normal tables already exist", message)
        self.assertNotIn("ai/alembic.ini", message)


if __name__ == "__main__":
    unittest.main()
