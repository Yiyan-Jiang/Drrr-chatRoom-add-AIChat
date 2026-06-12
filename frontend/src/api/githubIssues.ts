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

export const githubIssuesApi = {
  list: async (): Promise<MessageBoardIssue[]> => {
    const { data } = await apiClient.get<MessageBoardIssue[]>('/github/issues')
    return data
  },
  get: async (issueNumber: number): Promise<MessageBoardIssue> => {
    const { data } = await apiClient.get<MessageBoardIssue>(`/github/issues/${issueNumber}`)
    return data
  },
  listComments: async (issueNumber: number): Promise<MessageBoardIssueComment[]> => {
    const { data } = await apiClient.get<MessageBoardIssueComment[]>(`/github/issues/${issueNumber}/comments`)
    return data
  },
}
