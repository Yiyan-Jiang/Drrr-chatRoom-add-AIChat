from pathlib import Path
import unittest
from unittest.mock import patch


class NormalSystemRepositoryBoundaryTest(unittest.TestCase):
    def test_normal_system_repositories_exports_existing_api(self):
        with patch.dict(
            "os.environ",
            {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms"},
        ):
            from normal_system.repositories import (
                create_message,
                create_room,
                create_user,
                get_room_by_id,
                get_user_by_id,
                serialize_message,
            )

        exported = {
            create_message,
            create_room,
            create_user,
            get_room_by_id,
            get_user_by_id,
            serialize_message,
        }

        self.assertEqual(len(exported), 6)

    def test_normal_routers_import_normal_system_repositories(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "normal_system" / "routers" / "auth.py",
            root / "normal_system" / "routers" / "message.py",
            root / "normal_system" / "routers" / "room.py",
            root / "normal_system" / "routers" / "socket.py",
            root / "normal_system" / "routers" / "user.py",
        ]

        joined = "\n".join(path.read_text(encoding="utf-8") for path in files)

        self.assertIn("normal_system.repositories", joined)
        self.assertNotIn("from crud import", joined)


if __name__ == "__main__":
    unittest.main()
