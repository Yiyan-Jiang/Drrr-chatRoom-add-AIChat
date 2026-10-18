"""请求 GitHub API，转换上游错误并缓存查询结果。"""

import os
from time import monotonic
from typing import Any

import httpx


GITHUB_CACHE_TTL_SECONDS = 60.0
_github_cache: dict[
    tuple[str, tuple[tuple[str, str], ...], str, str], tuple[float, Any]
] = {}


class GitHubAPIError(Exception):
    """携带可映射为 HTTP 响应的 GitHub 上游错误。"""

    def __init__(self, status_code: int, detail: str):
        """保存上游错误映射后的 HTTP 状态码和错误说明。"""
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _github_repository() -> tuple[str, str]:
    """读取 GitHub 仓库配置，未配置时使用项目默认仓库。"""
    owner = os.getenv("GITHUB_ISSUES_OWNER", "Yiyan-Jiang")
    repo = os.getenv("GITHUB_ISSUES_REPO", "Drrr-chatRoom-add-AIChat")
    return owner, repo


def _github_headers() -> dict[str, str]:
    """构造 GitHub 请求头，仅在配置令牌时添加认证信息。"""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get_json_from_github(url: str, params: dict[str, Any] | None = None) -> Any:
    """从短期缓存或 GitHub API 读取 JSON 响应。

    Args:
        url: GitHub API 请求地址。
        params: 可选查询参数，同时参与缓存键计算。

    Returns:
        HTTP 响应解析后的 JSON 数据，或仍在有效期内的缓存数据。

    Raises:
        GitHubAPIError: 上游请求失败；上游认证失败不会映射为本地 JWT 失效。
    """
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
            # 上游凭证错误与当前用户的本地 JWT 会话无关。
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
        raise GitHubAPIError(
            status_code=exc.response.status_code, detail=detail
        ) from exc
    except httpx.HTTPError as exc:
        raise GitHubAPIError(
            status_code=502,
            detail="Unable to connect to GitHub API.",
        ) from exc

    payload = response.json()
    _github_cache[cache_key] = (now, payload)
    return payload
