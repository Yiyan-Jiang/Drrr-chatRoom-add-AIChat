import os
from time import monotonic
from typing import Any

import httpx


GITHUB_CACHE_TTL_SECONDS = 60.0
_github_cache: dict[tuple[str, tuple[tuple[str, str], ...], str, str], tuple[float, Any]] = {}


class GitHubAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _github_repository() -> tuple[str, str]:
    owner = os.getenv("GITHUB_ISSUES_OWNER", "Yiyan-Jiang")
    repo = os.getenv("GITHUB_ISSUES_REPO", "Drrr-chatRoom-add-AIChat")
    return owner, repo


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get_json_from_github(url: str, params: dict[str, Any] | None = None) -> Any:
    owner, repo = _github_repository()
    normalized_params = tuple(
        sorted((key, str(value)) for key, value in (params or {}).items())
    )
    cache_key = (url, normalized_params, owner, repo)
    now = monotonic()
    cached = _github_cache.get(cache_key)
    if cached and now - cached[0] < GITHUB_CACHE_TTL_SECONDS:
        return cached[1]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                params=params,
                headers=_github_headers(),
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            # Upstream credentials are unrelated to the user's local JWT session.
            raise GitHubAPIError(
                status_code=502,
                detail="GitHub authentication failed. Check the server GITHUB_TOKEN configuration.",
            ) from exc
        if exc.response.status_code == 403:
            detail = "GitHub API request limit reached. Please try again later."
        elif exc.response.status_code == 404:
            detail = "GitHub repository or issues endpoint was not found."
        else:
            detail = "GitHub API request failed."
        raise GitHubAPIError(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise GitHubAPIError(
            status_code=502,
            detail="Unable to connect to GitHub API.",
        ) from exc

    payload = response.json()
    _github_cache[cache_key] = (now, payload)
    return payload
