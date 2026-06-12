from pathlib import Path
import unittest
from unittest.mock import patch


class NormalSystemRouterBoundaryTest(unittest.TestCase):
    def test_normal_system_routers_exports_app_routers_and_socket(self):
        with patch.dict(
            "os.environ",
            {
                "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
                "CHAT_JWT_SECRET": "secret",
            },
        ):
            from normal_system.routers import (
                auth_router,
                gate_router,
                github_router,
                message_router,
                room_router,
                socket_io_server,
                user_router,
            )

        self.assertIsNotNone(auth_router)
        self.assertIsNotNone(gate_router)
        self.assertIsNotNone(github_router)
        self.assertIsNotNone(message_router)
        self.assertIsNotNone(room_router)
        self.assertIsNotNone(socket_io_server)
        self.assertIsNotNone(user_router)

    def test_root_router_package_is_removed(self):
        root = Path(__file__).resolve().parents[1]

        self.assertFalse((root / "routers" / "__init__.py").exists())

    def test_room_router_uses_normal_system_socket_module(self):
        root = Path(__file__).resolve().parents[1]
        room_router = (root / "normal_system" / "routers" / "room.py").read_text(encoding="utf-8")

        self.assertIn("normal_system.routers.socket", room_router)
        self.assertNotIn("from routers.socket import", room_router)


if __name__ == "__main__":
    unittest.main()
