import ast
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_github_route_and_client_have_separate_responsibilities():
    route = (ROOT / "normal_system/routers/github.py").read_text(encoding="utf-8")
    assert "httpx" not in route
    assert "_github_cache" not in route
    client_path = ROOT / "normal_system/integrations/github.py"
    assert client_path.exists()
    imports = [
        node.module for node in ast.walk(ast.parse(client_path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom)
    ]
    assert not any(name and name.startswith(("fastapi", "normal_system.routers")) for name in imports)


@pytest.mark.parametrize("status,expected,detail", [
    (401, 502, "GitHub authentication failed. Check the server GITHUB_TOKEN configuration."),
    (403, 403, "GitHub API request limit reached. Please try again later."),
    (404, 404, "GitHub repository or issues endpoint was not found."),
    (500, 500, "GitHub API request failed."),
])
def test_github_client_preserves_upstream_error_status_and_detail(status, expected, detail):
    assert (ROOT / "normal_system/integrations/github.py").exists()
    from normal_system.integrations import github

    async def scenario():
        response = httpx.Response(status, request=httpx.Request("GET", "https://api.github.com/test"))
        upstream = AsyncMock()
        upstream.__aenter__.return_value.get.return_value = response
        with patch.object(github, "_github_cache", {}), patch.object(github.httpx, "AsyncClient", return_value=upstream):
            with pytest.raises(github.GitHubAPIError) as error:
                await github._get_json_from_github("https://api.github.com/test")
        assert error.value.status_code == expected
        assert error.value.detail == detail

    asyncio.run(scenario())


def test_github_client_preserves_network_error():
    assert (ROOT / "normal_system/integrations/github.py").exists()
    from normal_system.integrations import github

    async def scenario():
        upstream = AsyncMock()
        upstream.__aenter__.return_value.get.side_effect = httpx.ConnectError("offline")
        with patch.object(github, "_github_cache", {}), patch.object(github.httpx, "AsyncClient", return_value=upstream):
            with pytest.raises(github.GitHubAPIError) as error:
                await github._get_json_from_github("https://api.github.com/test")
        assert error.value.status_code == 502
        assert error.value.detail == "Unable to connect to GitHub API."

    asyncio.run(scenario())


def test_github_service_filters_pull_requests_and_preserves_field_defaults():
    from normal_system.services import github

    async def scenario():
        issue = {
            "id": 9, "number": 3, "title": "issue", "body": None,
            "html_url": "https://github.com/test/issues/3", "comments": 0,
            "state": "open", "created_at": "created", "updated_at": "updated", "user": None,
        }
        with patch.object(github.client, "_get_json_from_github", AsyncMock(return_value=[
            {"pull_request": {"url": "https://github.com/test/pull/1"}}, issue,
        ])):
            items = await github.list_github_issues()
        assert len(items) == 1
        assert items[0]["id"] == 9
        assert items[0]["body"] == ""
        assert items[0]["author"] == {
            "login": "unknown", "avatarUrl": "", "profileUrl": issue["html_url"],
        }
        with patch.object(github.client, "_get_json_from_github", AsyncMock(return_value={"pull_request": {"url": "test"}})):
            with pytest.raises(github.client.GitHubAPIError) as error:
                await github.get_github_issue(1)
        assert error.value.status_code == 404
        assert error.value.detail == "GitHub issue was not found."

    asyncio.run(scenario())
