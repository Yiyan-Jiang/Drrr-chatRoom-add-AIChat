import importlib
import os
import sys
import unittest
from importlib import import_module
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.routing import APIRoute


class GitHubIssuesProxyTest(unittest.IsolatedAsyncioTestCase):
    def test_main_mounts_github_issues_proxy_route(self):
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
          main = importlib.import_module("main")

      routes = {
          (route.path, method)
          for route in main.app.routes
          if isinstance(route, APIRoute)
          for method in route.methods
      }

      self.assertIn(("/api/github/issues", "GET"), routes)
      self.assertIn(("/api/github/issues/{issue_number}", "GET"), routes)
      self.assertIn(("/api/github/issues/{issue_number}/comments", "GET"), routes)

    async def test_proxy_reads_repository_and_token_from_environment(self):
        from normal_system.routers.github import list_github_issues

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [
            {
                "id": 101,
                "number": 7,
                "title": "Message board",
                "body": "hello",
                "html_url": "https://github.com/example/private-repo/issues/7",
                "comments": 2,
                "state": "open",
                "created_at": "2026-06-07T10:00:00Z",
                "updated_at": "2026-06-08T10:00:00Z",
                "user": {
                    "login": "octocat",
                    "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                    "html_url": "https://github.com/octocat",
                },
            }
        ]
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.__aenter__.return_value.get.return_value = response

        with patch.dict(
            os.environ,
            {
                "GITHUB_ISSUES_OWNER": "example",
                "GITHUB_ISSUES_REPO": "private-repo",
                "GITHUB_TOKEN": "secret-token",
            },
            clear=False,
        ), patch("normal_system.routers.github.httpx.AsyncClient", return_value=client):
            issues = await list_github_issues()

        get_call = client.__aenter__.return_value.get
        url = get_call.call_args.args[0]
        kwargs = get_call.call_args.kwargs

        self.assertEqual(
            url,
            "https://api.github.com/repos/example/private-repo/issues",
        )
        self.assertEqual(kwargs["params"]["state"], "all")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer secret-token")
        self.assertEqual(issues[0]["author"]["login"], "octocat")
        self.assertNotIn("secret-token", str(issues))

    async def test_proxy_fetches_single_issue_by_number(self):
        from normal_system.routers.github import get_github_issue

        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "id": 101,
            "number": 7,
            "title": "Message board",
            "body": "hello",
            "html_url": "https://github.com/example/private-repo/issues/7",
            "comments": 2,
            "state": "open",
            "created_at": "2026-06-07T10:00:00Z",
            "updated_at": "2026-06-08T10:00:00Z",
            "user": {
                "login": "octocat",
                "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
                "html_url": "https://github.com/octocat",
            },
        }

        client = AsyncMock()
        client.__aenter__.return_value.get.return_value = response

        with patch.dict(
            os.environ,
            {
                "GITHUB_ISSUES_OWNER": "example",
                "GITHUB_ISSUES_REPO": "private-repo",
            },
            clear=False,
        ), patch("normal_system.routers.github.httpx.AsyncClient", return_value=client):
            issue = await get_github_issue(7)

        get_call = client.__aenter__.return_value.get
        self.assertEqual(
            get_call.call_args.args[0],
            "https://api.github.com/repos/example/private-repo/issues/7",
        )
        self.assertEqual(issue["number"], 7)
        self.assertEqual(issue["title"], "Message board")

    async def test_proxy_fetches_issue_comments_by_number(self):
        from normal_system.routers.github import list_github_issue_comments

        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        response.json.return_value = [
            {
                "id": 301,
                "body": "comment body",
                "html_url": "https://github.com/example/private-repo/issues/7#issuecomment-301",
                "created_at": "2026-06-08T10:00:00Z",
                "updated_at": "2026-06-08T10:30:00Z",
                "user": {
                    "login": "commenter",
                    "avatar_url": "https://avatars.githubusercontent.com/u/2?v=4",
                    "html_url": "https://github.com/commenter",
                },
            }
        ]

        client = AsyncMock()
        client.__aenter__.return_value.get.return_value = response

        with patch.dict(
            os.environ,
            {
                "GITHUB_ISSUES_OWNER": "example",
                "GITHUB_ISSUES_REPO": "private-repo",
            },
            clear=False,
        ), patch("normal_system.routers.github.httpx.AsyncClient", return_value=client):
            comments = await list_github_issue_comments(7)

        get_call = client.__aenter__.return_value.get
        self.assertEqual(
            get_call.call_args.args[0],
            "https://api.github.com/repos/example/private-repo/issues/7/comments",
        )
        self.assertEqual(comments[0]["author"]["login"], "commenter")
        self.assertEqual(comments[0]["body"], "comment body")

    async def test_github_json_requests_are_cached_within_ttl(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "mysql+aiomysql://user:pass@localhost:3306/chat_rooms",
                "CHAT_JWT_SECRET": "secret",
            },
            clear=False,
        ):
            github = import_module("normal_system.routers.github")

        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        response.json.return_value = [{"id": 1}]

        client = AsyncMock()
        client.__aenter__.return_value.get.return_value = response

        with patch.object(github, "_github_cache", {}), patch.object(
            github,
            "monotonic",
            side_effect=[100.0, 120.0, 161.0],
        ), patch("normal_system.routers.github.httpx.AsyncClient", return_value=client):
            first = await github._get_json_from_github("https://api.github.com/example")
            second = await github._get_json_from_github("https://api.github.com/example")
            third = await github._get_json_from_github("https://api.github.com/example")

        self.assertEqual(first, [{"id": 1}])
        self.assertEqual(second, [{"id": 1}])
        self.assertEqual(third, [{"id": 1}])
        self.assertEqual(client.__aenter__.return_value.get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
