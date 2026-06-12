import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import {
  mapGitHubIssueCommentList,
  mapGitHubIssueList,
  mapGitHubIssueToMessageBoardIssue,
} from '../src/api/githubIssueMappers.js'

const testDir = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(testDir, '..', '..', '..')

const baseIssue = {
  id: 101,
  number: 7,
  title: 'Add message board',
  body: '## Hello\nThis is a GitHub issue.',
  html_url: 'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/issues/7',
  comments: 3,
  state: 'open',
  created_at: '2026-06-07T10:00:00Z',
  updated_at: '2026-06-08T10:00:00Z',
  user: {
    login: 'octocat',
    avatar_url: 'https://avatars.githubusercontent.com/u/1?v=4',
    html_url: 'https://github.com/octocat',
  },
} as const

test('maps GitHub issue fields into message board issue fields', () => {
  const issue = mapGitHubIssueToMessageBoardIssue(baseIssue)

  assert.equal(issue.id, 101)
  assert.equal(issue.number, 7)
  assert.equal(issue.title, 'Add message board')
  assert.equal(issue.body, '## Hello\nThis is a GitHub issue.')
  assert.equal(
    issue.htmlUrl,
    'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/issues/7',
  )
  assert.equal(issue.commentsCount, 3)
  assert.equal(issue.state, 'open')
  assert.deepEqual(issue.author, {
    login: 'octocat',
    avatarUrl: 'https://avatars.githubusercontent.com/u/1?v=4',
    profileUrl: 'https://github.com/octocat',
  })
})

test('maps null issue body to an empty string', () => {
  const issue = mapGitHubIssueToMessageBoardIssue({
    ...baseIssue,
    body: null,
  })

  assert.equal(issue.body, '')
})

test('filters pull requests out of GitHub issues response', () => {
  const issues = mapGitHubIssueList([
    baseIssue,
    {
      ...baseIssue,
      id: 202,
      number: 8,
      title: 'Pull request entry',
      pull_request: {
        html_url: 'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/pull/8',
      },
    },
  ])

  assert.equal(issues.length, 1)
  assert.equal(issues[0]?.number, 7)
})

test('front end requests the backend proxy instead of GitHub directly', () => {
  const source = readFileSync(
    resolve(projectRoot, 'src/api/githubIssues.ts'),
    'utf8',
  )

  assert.match(source, /apiClient\.get<MessageBoardIssue\[]>\('\/github\/issues'\)/)
  assert.match(source, /apiClient\.get<MessageBoardIssue>\(`\/github\/issues\/\$\{issueNumber\}`\)/)
  assert.match(source, /apiClient\.get<MessageBoardIssueComment\[]>\(`\/github\/issues\/\$\{issueNumber\}\/comments`\)/)
  assert.doesNotMatch(source, /api\.github\.com/)
  assert.doesNotMatch(source, /GITHUB_TOKEN/)
})

test('maps GitHub issue comments into message board comments', () => {
  const comments = mapGitHubIssueCommentList([
    {
      id: 301,
      body: 'comment body',
      html_url: 'https://github.com/example/repo/issues/7#issuecomment-301',
      created_at: '2026-06-08T10:00:00Z',
      updated_at: '2026-06-08T10:30:00Z',
      user: {
        login: 'commenter',
        avatar_url: 'https://avatars.githubusercontent.com/u/2?v=4',
        html_url: 'https://github.com/commenter',
      },
    },
    {
      id: 302,
      body: null,
      html_url: 'https://github.com/example/repo/issues/7#issuecomment-302',
      created_at: '2026-06-08T11:00:00Z',
      updated_at: '2026-06-08T11:30:00Z',
      user: null,
    },
  ])

  assert.equal(comments.length, 2)
  assert.deepEqual(comments[0], {
    id: 301,
    body: 'comment body',
    htmlUrl: 'https://github.com/example/repo/issues/7#issuecomment-301',
    createdAt: '2026-06-08T10:00:00Z',
    updatedAt: '2026-06-08T10:30:00Z',
    author: {
      login: 'commenter',
      avatarUrl: 'https://avatars.githubusercontent.com/u/2?v=4',
      profileUrl: 'https://github.com/commenter',
    },
  })
  assert.equal(comments[1]?.body, '')
  assert.equal(comments[1]?.author.login, 'unknown')
})
