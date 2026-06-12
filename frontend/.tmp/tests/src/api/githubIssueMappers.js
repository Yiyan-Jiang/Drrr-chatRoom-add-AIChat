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
export function mapGitHubIssueCommentList(comments) {
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
    }));
}
