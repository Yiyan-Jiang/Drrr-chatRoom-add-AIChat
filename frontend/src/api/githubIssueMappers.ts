/** 定义留言板数据，并将 GitHub Issue 响应转换为前端字段。 */
/** 留言或评论作者的 GitHub 公开资料。 */
export interface GitHubIssueAuthor {
  /** GitHub 用户名。 */
  login: string
  /** 作者头像地址。 */
  avatarUrl: string
  /** 作者主页地址。 */
  profileUrl: string
}

/** 供留言板页面展示的 Issue。 */
export interface MessageBoardIssue {
  /** 服务端记录编号。 */
  id: number
  /** Issue 在仓库内的编号。 */
  number: number
  /** 留言标题。 */
  title: string
  /** Markdown 正文。 */
  body: string
  /** GitHub 页面地址。 */
  htmlUrl: string
  /** 留言评论数量。 */
  commentsCount: number
  /** Issue 的打开或关闭状态。 */
  state: 'open' | 'closed'
  /** 创建时间字符串。 */
  createdAt: string
  /** 最近更新时间字符串。 */
  updatedAt: string
  /** 留言作者的 GitHub 公开资料。 */
  author: GitHubIssueAuthor
}

/** 供留言详情页展示的评论。 */
export interface MessageBoardIssueComment {
  /** 服务端记录编号。 */
  id: number
  /** Markdown 正文。 */
  body: string
  /** GitHub 页面地址。 */
  htmlUrl: string
  /** 创建时间字符串。 */
  createdAt: string
  /** 最近更新时间字符串。 */
  updatedAt: string
  /** 评论作者的 GitHub 公开资料。 */
  author: GitHubIssueAuthor
}

/** GitHub 原始响应中的用户摘要。 */
interface GitHubIssueUserResponse {
  /** GitHub 用户名。 */
  login: string
  /** GitHub 用户头像地址。 */
  avatar_url: string
  /** GitHub 页面地址。 */
  html_url: string
}

/** GitHub Issue 列表或详情接口的原始字段。 */
export interface GitHubIssueResponse {
  /** 服务端记录编号。 */
  id: number
  /** Issue 在仓库内的编号。 */
  number: number
  /** Issue 标题。 */
  title: string
  /** Markdown 正文。 */
  body: string | null
  /** GitHub 页面地址。 */
  html_url: string
  /** Issue 评论数量。 */
  comments: number
  /** Issue 的打开或关闭状态。 */
  state: 'open' | 'closed'
  /** 服务端创建时间字符串。 */
  created_at: string
  /** 服务端最近更新时间字符串。 */
  updated_at: string
  /** 对应用户的资料。 */
  user: GitHubIssueUserResponse | null
  /** GitHub 返回的 Pull Request 标记，用于从留言列表中过滤此类记录。 */
  pull_request?: unknown
}

/** GitHub Issue 评论接口的原始字段。 */
export interface GitHubIssueCommentResponse {
  /** 服务端记录编号。 */
  id: number
  /** Markdown 正文。 */
  body: string | null
  /** GitHub 页面地址。 */
  html_url: string
  /** 服务端创建时间字符串。 */
  created_at: string
  /** 服务端最近更新时间字符串。 */
  updated_at: string
  /** 对应用户的资料。 */
  user: GitHubIssueUserResponse | null
}

/**
 * 转换单条 GitHub Issue 字段，并为缺失正文和作者资料填入显示用文本。
 * @param issue - GitHub Issue 原始响应。
 * @returns 留言板使用的留言模型。
 */
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

/**
 * 过滤 Pull Request，再转换 GitHub Issue 列表。
 * @param issues - GitHub 返回的 Issue 列表。
 * @returns 留言板留言数组。
 */
export function mapGitHubIssueList(
  issues: GitHubIssueResponse[],
): MessageBoardIssue[] {
  return issues
    .filter((issue) => !issue.pull_request)
    .map(mapGitHubIssueToMessageBoardIssue)
}

/**
 * 转换 GitHub 评论列表，并补齐缺失正文与作者展示字段。
 * @param comments - GitHub 评论原始响应数组。
 * @returns 留言板评论数组。
 */
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
