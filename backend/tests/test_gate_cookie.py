import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


GATE_COOKIE_SECRET = "gate-cookie-secret-with-at-least-32-bytes"


class GateCookieTest(unittest.TestCase):
    def test_gate_status_rejects_plain_true_cookie(self):
        with gate_test_environment():
            from normal_system.routers.gate import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            client.cookies.set("gate_passed", "true")

            response = client.get("/gate/status")

        self.assertEqual(response.status_code, 401)

    def test_gate_verify_sets_signed_local_dev_cookie_that_status_accepts(self):
        with gate_test_environment():
            from normal_system.routers.gate import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app, base_url="https://testserver")

            verify_response = client.post("/gate/verify", data={"password": "gate"})
            status_response = client.get("/gate/status")

        self.assertEqual(verify_response.status_code, 200)
        cookie_header = verify_response.headers["set-cookie"]
        self.assertIn("gate_passed=", cookie_header)
        self.assertIn("HttpOnly", cookie_header)
        self.assertNotIn("Secure", cookie_header)
        self.assertNotIn("gate_passed=true", cookie_header)
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json(), {"verified": True})

    def test_gate_verify_falls_back_to_jwt_secret_for_existing_local_env(self):
        with gate_test_environment(include_gate_cookie_secret=False):
            from normal_system.routers.gate import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)

            verify_response = client.post("/gate/verify", data={"password": "gate"})
            status_response = client.get("/gate/status")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(status_response.status_code, 200)

    def test_gate_dependency_accepts_signed_cookie_and_rejects_tampering(self):
        with gate_test_environment():
            from common.dependencies import require_gate_passed
            from common.gate_cookie import create_gate_cookie_value

            valid_cookie = create_gate_cookie_value(secret=GATE_COOKIE_SECRET)
            tampered_cookie = f"{valid_cookie}x"

            run_async(require_gate_passed(FakeRequest({"gate_passed": valid_cookie})))
            with self.assertRaises(HTTPException) as ctx:
                run_async(require_gate_passed(FakeRequest({"gate_passed": tampered_cookie})))

        self.assertEqual(ctx.exception.status_code, 401)


class FakeRequest:
    def __init__(self, cookies):
        self.cookies = cookies


def run_async(coro):
    import asyncio

    return asyncio.run(coro)


def gate_test_environment(include_gate_cookie_secret=True):
    values = {
        "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
        "AI_DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/ai_chat",
        "CHAT_JWT_SECRET": "jwt-secret-with-at-least-32-bytes",
        "CHAT_GATE_PASSWORD": "gate",
        "USERNAME": "test-user",
    }
    if include_gate_cookie_secret:
        values["CHAT_GATE_COOKIE_SECRET"] = GATE_COOKIE_SECRET

    return patch.dict(
        os.environ,
        values,
        clear=True,
    )


if __name__ == "__main__":
    unittest.main()
