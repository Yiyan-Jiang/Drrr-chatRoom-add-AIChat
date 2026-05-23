from pathlib import Path
import unittest
from unittest.mock import patch


class NormalSystemModelBoundaryTest(unittest.TestCase):
    def test_normal_system_models_exports_tables(self):
        with patch.dict(
            "os.environ",
            {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms"},
        ):
            from normal_system.models import Message, Room, User

        self.assertEqual(User.__tablename__, "chatRoom_user")
        self.assertEqual(Room.__tablename__, "chatRoom_room")
        self.assertEqual(Message.__tablename__, "chatRoom_message")

    def test_backend_modules_import_normal_system_models(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "common" / "normal_database.py",
            root / "normal_system" / "alembic" / "env.py",
        ]

        joined = "\n".join(path.read_text(encoding="utf-8") for path in files)

        self.assertIn("normal_system.models", joined)
        self.assertNotIn("from models import", joined)
        self.assertNotIn("import models", joined)


if __name__ == "__main__":
    unittest.main()
