/** 通过后端代理查询 GitHub 留言板及评论，并导出数据转换接口。 */
import { apiClient } from './client.js'
import type {
  MessageBoardIssue,
  MessageBoardIssueComment,
} from './githubIssueMappers.js'
export type {
  GitHubIssueAuthor,
  GitHubIssueCommentResponse,
  GitHubIssueResponse,
  MessageBoardIssue,
  MessageBoardIssueComment,
} from './githubIssueMappers.js'
export {
  mapGitHubIssueCommentList,
  mapGitHubIssueList,
  mapGitHubIssueToMessageBoardIssue,
} from './githubIssueMappers.js'

/** 留言板查询接口。 */
export const githubIssuesApi = {
  /**
   * 查询留言板 Issue 列表。
   * @returns 留言数组。
   */
  list: async (): Promise<MessageBoardIssue[]> => {
    const { data } = await apiClient.get<MessageBoardIssue[]>('/github/issues')
    return data
  },
  /**
   * 查询指定留言的详情。
   * @param issueNumber - Issue 在仓库中的编号。
   * @returns 留言详情。
   */
  get: async (issueNumber: number): Promise<MessageBoardIssue> => {
    const { data } = await apiClient.get<MessageBoardIssue>(
      `/github/issues/${issueNumber}`,
    )
    return data
  },
  /**
   * 查询指定留言的评论。
   * @param issueNumber - Issue 在仓库中的编号。
   * @returns 评论数组。
   */
  listComments: async (
    issueNumber: number,
  ): Promise<MessageBoardIssueComment[]> => {
    const { data } = await apiClient.get<MessageBoardIssueComment[]>(
      `/github/issues/${issueNumber}/comments`,
    )
    return data
  },
}
