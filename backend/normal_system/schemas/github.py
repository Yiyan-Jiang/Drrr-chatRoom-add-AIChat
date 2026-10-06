from typing import Literal

from pydantic import BaseModel


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
