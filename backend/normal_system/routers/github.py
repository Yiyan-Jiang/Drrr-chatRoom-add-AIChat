import os
from time import monotonic
from typing import Any, Literal

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/github", tags=["github"])
GITHUB_CACHE_TTL_SECONDS = 60.0
_github_cache: dict[tuple[str, tuple[tuple[str, str], ...], str, str], tuple[float, Any]] = {}


class GitHubIssueAuthor(BaseModel):
    login: str
    avatarUrl: str
    profileUrl: str


class GitHubIssue(BaseModel):
    id: int
    number: int
    title: str
    body: str
    htmlUrl: str
    commentsCount: int
    state: Literal["open", "closed"]
    createdAt: str
    updatedAt: str
    author: GitHubIssueAuthor


class GitHubIssueComment(BaseModel):
    id: int
    body: str
    htmlUrl: str
    createdAt: str
    updatedAt: str
    author: GitHubIssueAuthor


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


def _map_issue(issue: dict[str, Any]) -> dict[str, Any]:
    user = issue.get("user") or {}
    return {
        "id": issue["id"],
        "number": issue["number"],
        "title": issue["title"],
        "body": issue.get("body") or "",
        "htmlUrl": issue["html_url"],
        "commentsCount": issue["comments"],
        "state": issue["state"],
        "createdAt": issue["created_at"],
        "updatedAt": issue["updated_at"],
        "author": {
            "login": user.get("login") or "unknown",
            "avatarUrl": user.get("avatar_url") or "",
            "profileUrl": user.get("html_url") or issue["html_url"],
        },
    }


def _map_comment(comment: dict[str, Any]) -> dict[str, Any]:
    user = comment.get("user") or {}
    return {
        "id": comment["id"],
        "body": comment.get("body") or "",
        "htmlUrl": comment["html_url"],
        "createdAt": comment["created_at"],
        "updatedAt": comment["updated_at"],
        "author": {
            "login": user.get("login") or "unknown",
            "avatarUrl": user.get("avatar_url") or "",
            "profileUrl": user.get("html_url") or comment["html_url"],
        },
    }


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
        if exc.response.status_code == status.HTTP_403_FORBIDDEN:
            detail = "GitHub API request limit reached. Please try again later."
        elif exc.response.status_code == status.HTTP_404_NOT_FOUND:
            detail = "GitHub repository or issues endpoint was not found."
        else:
            detail = "GitHub API request failed."
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to connect to GitHub API.",
        ) from exc

    payload = response.json()
    _github_cache[cache_key] = (now, payload)
    return payload


@router.get("/issues", response_model=list[GitHubIssue])
async def list_github_issues() -> list[dict[str, Any]]:
    owner, repo = _github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    issues = await _get_json_from_github(
        url,
        params={
            "state": "all",
            "per_page": 20,
            "sort": "updated",
            "direction": "desc",
        },
    )
    return [
        _map_issue(issue)
        for issue in issues
        if not issue.get("pull_request")
    ]


@router.get("/issues/{issue_number}", response_model=GitHubIssue)
async def get_github_issue(issue_number: int) -> dict[str, Any]:
    owner, repo = _github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    issue = await _get_json_from_github(url)
    if issue.get("pull_request"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub issue was not found.",
        )
    return _map_issue(issue)


@router.get("/issues/{issue_number}/comments", response_model=list[GitHubIssueComment])
async def list_github_issue_comments(issue_number: int) -> list[dict[str, Any]]:
    owner, repo = _github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    comments = await _get_json_from_github(
        url,
        params={
            "per_page": 50,
        },
    )
    return [_map_comment(comment) for comment in comments]
