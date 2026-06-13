export interface GitHubIssueAuthor {
  login: string
  avatarUrl: string
  profileUrl: string
}

export interface MessageBoardIssue {
  id: number
  number: number
  title: string
  body: string
  htmlUrl: string
  commentsCount: number
  state: 'open' | 'closed'
  createdAt: string
  updatedAt: string
  author: GitHubIssueAuthor
}

export interface MessageBoardIssueComment {
  id: number
  body: string
  htmlUrl: string
  createdAt: string
  updatedAt: string
  author: GitHubIssueAuthor
}

interface GitHubIssueUserResponse {
  login: string
  avatar_url: string
  html_url: string
}

export interface GitHubIssueResponse {
  id: number
  number: number
  title: string
  body: string | null
  html_url: string
  comments: number
  state: 'open' | 'closed'
  created_at: string
  updated_at: string
  user: GitHubIssueUserResponse | null
  pull_request?: unknown
}

export interface GitHubIssueCommentResponse {
  id: number
  body: string | null
  html_url: string
  created_at: string
  updated_at: string
  user: GitHubIssueUserResponse | null
}

export function mapGitHubIssueToMessageBoardIssue(
  issue: GitHubIssueResponse,
): MessageBoardIssue {
  return {
    id: issue.id,
    number: issue.number,
    title: issue.title,
    body: issue.body ?? '',
    htmlUrl: issue.html_url,
    commentsCount: issue.comments,
    state: issue.state,
    createdAt: issue.created_at,
    updatedAt: issue.updated_at,
    author: {
      login: issue.user?.login ?? 'unknown',
      avatarUrl: issue.user?.avatar_url ?? '',
      profileUrl: issue.user?.html_url ?? issue.html_url,
    },
  }
}

export function mapGitHubIssueList(
  issues: GitHubIssueResponse[],
): MessageBoardIssue[] {
  return issues
    .filter((issue) => !issue.pull_request)
    .map(mapGitHubIssueToMessageBoardIssue)
}

export function mapGitHubIssueCommentList(
  comments: GitHubIssueCommentResponse[],
): MessageBoardIssueComment[] {
  return comments.map((comment) => ({
    id: comment.id,
    body: comment.body ?? '',
    htmlUrl: comment.html_url,
    createdAt: comment.created_at,
    updatedAt: comment.updated_at,
    author: {
      login: comment.user?.login ?? 'unknown',
      avatarUrl: comment.user?.avatar_url ?? '',
      profileUrl: comment.user?.html_url ?? comment.html_url,
    },
  }))
}
