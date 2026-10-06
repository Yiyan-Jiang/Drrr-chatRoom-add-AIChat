from typing import Any

from fastapi import APIRouter, HTTPException

from normal_system.integrations.github import GitHubAPIError
from normal_system.schemas.github import GitHubIssue, GitHubIssueComment
from normal_system.services import github as service


router = APIRouter(prefix="/github", tags=["github"])


@router.get("/issues", response_model=list[GitHubIssue])
async def list_github_issues() -> list[dict[str, Any]]:
    try:
        return await service.list_github_issues()
    except GitHubAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/issues/{issue_number}", response_model=GitHubIssue)
async def get_github_issue(issue_number: int) -> dict[str, Any]:
    try:
        return await service.get_github_issue(issue_number)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/issues/{issue_number}/comments", response_model=list[GitHubIssueComment])
async def list_github_issue_comments(issue_number: int) -> list[dict[str, Any]]:
    try:
        return await service.list_github_issue_comments(issue_number)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
