from pathlib import Path
import unittest


class BackendFinalBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_root_compatibility_modules_are_removed(self):
        removed_paths = [
            "auth_token.py",
            "crud.py",
            "database.py",
            "dependencies.py",
            "models.py",
            "room_presence.py",
            "schemas.py",
            "routers/__init__.py",
            "routers/auth.py",
            "routers/gate.py",
            "routers/message.py",
            "routers/room.py",
            "routers/socket.py",
            "routers/user.py",
            "services/__init__.py",
        ]

        for relative_path in removed_paths:
            with self.subTest(relative_path=relative_path):
                self.assertFalse((self.root / relative_path).exists())

    def test_main_imports_final_router_boundaries_directly(self):
        main = (self.root / "main.py").read_text(encoding="utf-8")

        self.assertIn("from ai.routers.chat import router as ai_router", main)
        self.assertIn("from normal_system.routers import", main)
        self.assertNotIn("from routers import", main)

    def test_room_presence_lives_under_normal_system_services(self):
        from normal_system.services.room_presence import RoomPresence

        presence = RoomPresence()
        self.assertEqual(presence.join("sid-1", 1, user_id=7), 1)
        self.assertEqual(presence.members(1), [7])


if __name__ == "__main__":
    unittest.main()
