import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import { githubIssuesApi } from '@/api'
import type { MessageBoardIssue, MessageBoardIssueComment } from '@/api'
import { MarkdownRenderer } from '@/features/news/markdownRenderer'
import logoSource from '@/assets/icon/Logo/logo.png'

type LoadState = 'idle' | 'loading' | 'success' | 'error'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function getErrorMessage(error: unknown): string {
  const status = typeof error === 'object' && error !== null && 'response' in error
    ? (error as { response?: { status?: number } }).response?.status
    : undefined

  if (status === 403) {
    return 'GitHub API 请求次数暂时受限，请稍后再试。'
  }

  if (status === 404) {
    return '未找到这个 GitHub issue。'
  }

  return '暂时无法连接 GitHub，请稍后重试。'
}

function MarkdownBody({ body }: { body: string }) {
  if (!body) {
    return <p className="text-sm text-[#67676c]">没有正文。</p>
  }

  return (
    <div className="text-sm leading-7 text-[#3c3c43]">
      <MarkdownRenderer markdown={body} />
    </div>
  )
}

export default function MessageBoardIssueDetail() {
  const { issueNumber } = useParams()
  const parsedIssueNumber = Number(issueNumber)
  const [issue, setIssue] = useState<MessageBoardIssue | null>(null)
  const [comments, setComments] = useState<MessageBoardIssueComment[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const loadIssue = useCallback(async () => {
    if (!Number.isInteger(parsedIssueNumber) || parsedIssueNumber <= 0) {
      setLoadState('error')
      setErrorMessage('Issue 编号无效。')
      return
    }

    setLoadState('loading')
    setErrorMessage('')

    try {
      const [nextIssue, nextComments] = await Promise.all([
        githubIssuesApi.get(parsedIssueNumber),
        githubIssuesApi.listComments(parsedIssueNumber),
      ])
      setIssue(nextIssue)
      setComments(nextComments)
      setLoadState('success')
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
      setLoadState('error')
    }
  }, [parsedIssueNumber])

  useEffect(() => {
    void loadIssue()
  }, [loadIssue])

  const shell = (children: ReactNode) => (
    <main className="min-h-screen bg-[#f6f6f7] pt-14 text-[#213547]">
      <header className="fixed inset-x-0 top-0 z-40 border-b border-zinc-900 bg-black/95">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link className="flex min-w-0 items-center gap-3" to="/home/board">
            <img
              alt="Drrr logo"
              className="h-8 w-8 shrink-0 object-contain"
              src={logoSource}
            />
            <span className="truncate text-sm font-semibold text-zinc-100">
              Message Board
            </span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link
              className="text-zinc-400 transition hover:text-zinc-100"
              to="/home/board"
            >
              留言板
            </Link>
            <Link
              className="text-zinc-400 transition hover:text-zinc-100"
              to="/home/news"
            >
              新闻流
            </Link>
          </nav>
        </div>
      </header>
      {children}
    </main>
  )

  if (loadState === 'loading') {
    return shell(
      <section className="mx-auto flex max-w-4xl flex-col gap-4 px-4 py-5 sm:px-6">
        <div className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] px-4 py-8 text-center text-sm text-[#67676c]">
          正在加载 issue 详情...
        </div>
      </section>,
    )
  }

  if (loadState === 'error') {
    return shell(
      <section className="mx-auto flex max-w-4xl flex-col gap-4 px-4 py-5 sm:px-6">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-5">
          <p className="text-sm text-red-700">{errorMessage}</p>
          <button
            className="mt-4 rounded border border-red-200 px-3 py-1.5 text-sm text-red-700 transition hover:bg-red-100"
            type="button"
            onClick={loadIssue}
          >
            重试
          </button>
        </div>
      </section>,
    )
  }

  if (!issue) {
    return shell(
      <section className="mx-auto flex max-w-4xl flex-col gap-4 px-4 py-5 sm:px-6">
        <div className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] px-4 py-8 text-center text-sm text-[#67676c]">
          没有找到这条留言。
        </div>
      </section>,
    )
  }

  return shell(
    <section className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-5 sm:px-6">
      <Link
        className="w-fit text-sm font-medium text-[#3451b2] transition hover:text-[#213547]"
        to="/home/board"
      >
        返回留言板
      </Link>

      <article className="rounded-xl border border-[#e2e2e3] bg-[#ffffff] px-5 py-6 shadow-sm sm:px-8">
        <header className="border-b border-[#e2e2e3] pb-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
            <img
              className="h-12 w-12 shrink-0 rounded object-cover"
              src={issue.author.avatarUrl}
              alt={`${issue.author.login} avatar`}
              loading="lazy"
            />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2 text-xs text-[#67676c]">
                <span>#{issue.number}</span>
                <span>by {issue.author.login}</span>
                <span>更新于 {formatDate(issue.updatedAt)}</span>
                <span
                  className={`rounded-full px-2 py-0.5 ${
                    issue.state === 'open'
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'bg-[#f6f6f7] text-[#67676c]'
                  }`}
                >
                  {issue.state}
                </span>
              </div>
              <h1 className="mt-4 text-3xl font-bold tracking-tight text-[#213547]">
                {issue.title}
              </h1>
              <a
                className="mt-3 inline-block text-sm font-medium text-[#3451b2] underline-offset-2 hover:text-[#213547] hover:underline"
                href={issue.htmlUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                在 GitHub 查看
              </a>
            </div>
          </div>
        </header>

        <div className="mt-6">
          <MarkdownBody body={issue.body} />
        </div>
      </article>

      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between border-b border-[#e2e2e3] pb-2">
          <h2 className="text-base font-semibold text-[#213547]">
            评论 {comments.length}
          </h2>
        </div>

        {comments.length === 0 ? (
          <div className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] px-4 py-6 text-center text-sm text-[#67676c] shadow-sm">
            暂无评论。
          </div>
        ) : (
          comments.map((comment) => (
            <article
              className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] p-4 shadow-sm"
              key={comment.id}
            >
              <div className="flex gap-3">
                <img
                  className="h-9 w-9 shrink-0 rounded object-cover"
                  src={comment.author.avatarUrl}
                  alt={`${comment.author.login} avatar`}
                  loading="lazy"
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-[#67676c]">
                    {comment.author.login} · {formatDate(comment.updatedAt)}
                  </p>
                  <div className="mt-3">
                    <MarkdownBody body={comment.body} />
                  </div>
                </div>
              </div>
            </article>
          ))
        )}
      </section>
    </section>,
  )
}
