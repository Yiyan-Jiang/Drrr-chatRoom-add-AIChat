import os
from pathlib import Path
import unittest
from unittest.mock import patch


class Phase5DatabaseContractTest(unittest.TestCase):
    def test_sqlalchemy_metadata_contains_only_normal_business_tables(self):
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms"},
        ):
            import normal_system.models  # noqa: F401
            from common.normal_database import Login

        self.assertEqual(
            set(Login.metadata.tables),
            {
                "chatRoom_user",
                "chatRoom_room",
                "chatRoom_message",
                "chatRoom_friend_request",
                "chatRoom_friendship",
                "chatRoom_private_message",
                "chatRoom_post",
                "chatRoom_post_comment",
                "chatRoom_post_like",
                "chatRoom_post_favorite",
            },
        )

    def test_migration_files_only_manage_normal_business_tables(self):
        root = Path(__file__).resolve().parents[1]
        migrations = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (root / "normal_system" / "alembic" / "versions").glob("*.py")
        )
        for table in ("chatRoom_user", "chatRoom_room", "chatRoom_message",
                      "chatRoom_friendship", "chatRoom_private_message", "chatRoom_post"):
            with self.subTest(table=table):
                self.assertIn(table, migrations)
        self.assertNotIn("ai_chat_history", migrations)


if __name__ == "__main__":
    unittest.main()
