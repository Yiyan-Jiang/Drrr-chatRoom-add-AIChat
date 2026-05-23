from pathlib import Path
import unittest


class AlembicEnvLoadingTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_normal_alembic_env_loads_backend_dotenv(self):
        content = (self.root / "normal_system" / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("from dotenv import load_dotenv", content)
        self.assertIn('load_dotenv(Path(__file__).resolve().parents[2] / ".env")', content)

    def test_normal_alembic_env_supports_async_database_urls(self):
        content = (self.root / "normal_system" / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("import asyncio", content)
        self.assertIn("async_engine_from_config", content)
        self.assertIn("await connection.run_sync", content)
        self.assertIn("asyncio.run(run_async_migrations())", content)

    def test_ai_alembic_env_loads_backend_dotenv(self):
        content = (self.root / "ai" / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("from dotenv import load_dotenv", content)
        self.assertIn('load_dotenv(Path(__file__).resolve().parents[2] / ".env")', content)

    def test_ai_alembic_env_supports_async_database_urls(self):
        content = (self.root / "ai" / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("import asyncio", content)
        self.assertIn("async_engine_from_config", content)
        self.assertIn("await connection.run_sync", content)
        self.assertIn("asyncio.run(run_async_migrations())", content)


if __name__ == "__main__":
    unittest.main()
