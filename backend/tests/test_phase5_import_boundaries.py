from pathlib import Path
import unittest


class Phase5ImportBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def _read_package(self, package: str) -> str:
        package_root = self.root / package
        return "\n".join(
            path.read_text(encoding="utf-8")
            for path in package_root.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    def test_common_does_not_import_business_packages(self):
        common = self._read_package("common")

        self.assertNotIn("import normal_system", common)
        self.assertNotIn("from normal_system", common)
        self.assertNotIn("import ai", common)
        self.assertNotIn("from ai", common)

    def test_normal_system_does_not_import_ai_implementation(self):
        normal_system = self._read_package("normal_system")

        self.assertNotIn("from ai.", normal_system)
        self.assertNotIn("import ai.", normal_system)

    def test_ai_does_not_import_normal_system_business_layers(self):
        ai = self._read_package("ai")

        self.assertNotIn("from normal_system.repositories", ai)
        self.assertNotIn("from normal_system.services", ai)
        self.assertNotIn("from normal_system.models", ai)


if __name__ == "__main__":
    unittest.main()
