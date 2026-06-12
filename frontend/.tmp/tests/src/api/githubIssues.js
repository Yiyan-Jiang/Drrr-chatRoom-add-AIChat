import { apiClient } from './client.js';
export function mapGitHubIssueToMessageBoardIssue(issue) {
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
    };
}
export function mapGitHubIssueList(issues) {
    return issues
        .filter((issue) => !issue.pull_request)
        .map(mapGitHubIssueToMessageBoardIssue);
}
export const githubIssuesApi = {
    list: async () => {
        const { data } = await apiClient.get('/github/issues');
        return data;
    },
};
