"""定义 GitHub 议题与评论的对外响应结构。"""

from typing import Literal

from pydantic import BaseModel


class GitHubIssueAuthor(BaseModel):
    """返回 GitHub 作者的账号、头像和个人主页地址。"""

    login: str
    avatarUrl: str
    profileUrl: str


class GitHubIssue(BaseModel):
    """返回 GitHub 议题的内容、状态、统计和作者资料。"""

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
    """返回 GitHub 议题评论的内容、链接和作者资料。"""

    id: int
    body: str
    htmlUrl: str
    createdAt: str
    updatedAt: str
    author: GitHubIssueAuthor
