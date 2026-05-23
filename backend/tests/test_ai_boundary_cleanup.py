from pathlib import Path
import unittest


class AIBoundaryCleanupTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_legacy_ai_router_and_service_wrappers_are_removed(self):
        self.assertFalse((self.root / "routers" / "ai_chat.py").exists())
        self.assertFalse((self.root / "services" / "ai_chat.py").exists())

    def test_root_normal_compatibility_modules_are_removed(self):
        self.assertFalse((self.root / "models.py").exists())
        self.assertFalse((self.root / "crud.py").exists())
        self.assertFalse((self.root / "schemas.py").exists())


if __name__ == "__main__":
    unittest.main()
