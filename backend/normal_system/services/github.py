from typing import Any

from normal_system.integrations import github as client


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


async def list_github_issues() -> list[dict[str, Any]]:
    owner, repo = client._github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    issues = await client._get_json_from_github(
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


async def get_github_issue(issue_number: int) -> dict[str, Any]:
    owner, repo = client._github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    issue = await client._get_json_from_github(url)
    if issue.get("pull_request"):
        raise client.GitHubAPIError(
            status_code=404,
            detail="GitHub issue was not found.",
        )
    return _map_issue(issue)


async def list_github_issue_comments(issue_number: int) -> list[dict[str, Any]]:
    owner, repo = client._github_repository()
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    comments = await client._get_json_from_github(
        url,
        params={
            "per_page": 50,
        },
    )
    return [_map_comment(comment) for comment in comments]
