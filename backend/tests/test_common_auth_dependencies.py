import os
import base64
import json
import unittest
from unittest.mock import patch

from fastapi import HTTPException
import jwt

JWT_TEST_SECRET = "test-secret-with-at-least-32-bytes"


class CommonAuthDependenciesTest(unittest.TestCase):
    def test_common_auth_creates_and_decodes_access_token(self):
        from common.auth import create_access_token, decode_access_token

        with patch.dict(os.environ, {"CHAT_JWT_SECRET": JWT_TEST_SECRET}, clear=True):
            token, expires_in = create_access_token(42)

            self.assertEqual(expires_in, 3600)
            self.assertEqual(decode_access_token(token), 42)

    def test_common_auth_creates_standard_jwt_access_token(self):
        from common.auth import create_access_token

        with patch.dict(os.environ, {"CHAT_JWT_SECRET": JWT_TEST_SECRET}, clear=True):
            token, _expires_in = create_access_token(42)

        header_segment, _payload_segment, _signature_segment = token.split(".")
        padded_header = header_segment + "=" * (-len(header_segment) % 4)
        header = json.loads(base64.urlsafe_b64decode(padded_header).decode("utf-8"))

        self.assertEqual(header["typ"], "JWT")
        self.assertEqual(header["alg"], "HS256")

    def test_common_auth_uses_jwt_library_instead_of_manual_signing(self):
        root = os.path.dirname(os.path.dirname(__file__))
        auth_module = os.path.join(root, "common", "auth.py")

        with open(auth_module, encoding="utf-8") as file:
            source = file.read()

        self.assertIn("import jwt", source)
        self.assertNotIn("import hmac", source)
        self.assertNotIn("import hashlib", source)
        self.assertNotIn("urlsafe_b64", source)

    def test_common_auth_rejects_signed_token_without_expiration(self):
        from common.auth import decode_access_token

        token = jwt.encode({"sub": "42"}, JWT_TEST_SECRET, algorithm="HS256")

        with patch.dict(os.environ, {"CHAT_JWT_SECRET": JWT_TEST_SECRET}, clear=True):
            self.assertIsNone(decode_access_token(token))

    def test_common_dependency_rejects_missing_authorization(self):
        from common.dependencies import get_current_user_id

        with self.assertRaises(HTTPException) as ctx:
            run_async(get_current_user_id(authorization=None))

        self.assertEqual(ctx.exception.status_code, 401)

    def test_common_dependency_accepts_bearer_token(self):
        from common.auth import create_access_token
        from common.dependencies import get_current_user_id

        with patch.dict(os.environ, {"CHAT_JWT_SECRET": JWT_TEST_SECRET}, clear=True):
            token, _expires_in = create_access_token(7)
            user_id = run_async(get_current_user_id(authorization=f"Bearer {token}"))

        self.assertEqual(user_id, 7)

    def test_http_routers_import_common_auth_dependencies(self):
        root = os.path.dirname(os.path.dirname(__file__))
        files = [
            os.path.join(root, "normal_system", "routers", "auth.py"),
            os.path.join(root, "normal_system", "routers", "message.py"),
            os.path.join(root, "normal_system", "routers", "room.py"),
            os.path.join(root, "ai", "routers", "chat.py"),
        ]

        contents = []
        for path in files:
            with open(path, encoding="utf-8") as file:
                contents.append(file.read())
        joined = "\n".join(contents)

        self.assertIn("from common.auth import create_access_token", joined)
        self.assertIn("from common.dependencies import get_current_user_id", joined)
        self.assertNotIn("from auth_token import", joined)
        self.assertNotIn("from dependencies import", joined)
        self.assertNotIn("def get_current_user_id(authorization", joined)


def run_async(coro):
    import asyncio

    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
