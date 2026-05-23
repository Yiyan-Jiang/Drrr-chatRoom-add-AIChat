from pathlib import Path
import unittest


class NormalSystemSchemaBoundaryTest(unittest.TestCase):
    def test_normal_system_schemas_exports_public_dtos(self):
        from normal_system.schemas import (
            LoginRequest,
            LoginResponse,
            MessageCreate,
            MessageInDB,
            PaginatedMessagesResponse,
            RoomCreate,
            RoomInDB,
            RoomOwner,
            RoomUpdate,
            RoomWithMessages,
            UserCountResponse,
            UserCreate,
            UserInDB,
            UserPublic,
            UserUpdate,
        )

        exported = {
            LoginRequest,
            LoginResponse,
            MessageCreate,
            MessageInDB,
            PaginatedMessagesResponse,
            RoomCreate,
            RoomInDB,
            RoomOwner,
            RoomUpdate,
            RoomWithMessages,
            UserCountResponse,
            UserCreate,
            UserInDB,
            UserPublic,
            UserUpdate,
        }

        self.assertEqual(len(exported), 15)

    def test_normal_routers_import_normal_system_schemas(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "normal_system" / "routers" / "auth.py",
            root / "normal_system" / "routers" / "message.py",
            root / "normal_system" / "routers" / "room.py",
            root / "normal_system" / "routers" / "socket.py",
            root / "normal_system" / "routers" / "user.py",
        ]

        joined = "\n".join(path.read_text(encoding="utf-8") for path in files)

        self.assertIn("normal_system.schemas", joined)
        self.assertNotIn("from schemas import", joined)


if __name__ == "__main__":
    unittest.main()
