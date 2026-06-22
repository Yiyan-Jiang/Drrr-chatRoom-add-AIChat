import importlib
import os
import sys
import unittest
from unittest.mock import patch

from fastapi.routing import APIRoute


class Phase5APIContractTest(unittest.TestCase):
    def _load_main(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
                "AI_DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/ai_chat",
                "CHAT_JWT_SECRET": "secret",
                "CHAT_GATE_PASSWORD": "gate",
            },
        ):
            sys.modules.pop("main", None)
            return importlib.import_module("main")

    def test_http_api_routes_keep_public_contract(self):
        main = self._load_main()
        routes = {
            (route.path, method)
            for route in main.app.routes
            if isinstance(route, APIRoute)
            for method in route.methods
        }

        expected_routes = {
            ("/api/users/register", "POST"),
            ("/api/users/count", "GET"),
            ("/api/auth/login", "POST"),
            ("/api/gate/verify", "POST"),
            ("/api/gate/status", "GET"),
            ("/api/github/issues", "GET"),
            ("/api/github/issues/{issue_number}", "GET"),
            ("/api/github/issues/{issue_number}/comments", "GET"),
            ("/api/rooms/", "POST"),
            ("/api/rooms/", "GET"),
            ("/api/rooms/mine", "GET"),
            ("/api/rooms/viewers/count", "GET"),
            ("/api/rooms/{room_id:int}", "GET"),
            ("/api/rooms/{room_id:int}", "PATCH"),
            ("/api/rooms/{room_id:int}", "DELETE"),
            ("/api/messages/", "POST"),
            ("/api/messages/room/{room_id}", "GET"),
            ("/api/messages/room/{room_id}/page", "GET"),
            ("/api/ai/chat", "POST"),
            ("/api/ai/chat/history", "DELETE"),
            ("/api/ai/turn", "POST"),
        }

        self.assertTrue(expected_routes.issubset(routes))

    def test_room_dynamic_routes_only_match_integer_ids(self):
        main = self._load_main()
        room_routes = [
            route.path
            for route in main.app.routes
            if isinstance(route, APIRoute) and route.path.startswith("/api/rooms")
        ]

        self.assertIn("/api/rooms/mine", room_routes)
        self.assertIn("/api/rooms/{room_id:int}", room_routes)
        self.assertNotIn("/api/rooms/{room_id}", room_routes)

    def test_socket_events_keep_public_contract(self):
        from normal_system.routers import socket

        for event_name in (
            "connect",
            "disconnect",
            "join_room",
            "send_message",
            "leave_room",
        ):
            with self.subTest(event_name=event_name):
                self.assertTrue(hasattr(socket, event_name))


if __name__ == "__main__":
    unittest.main()
