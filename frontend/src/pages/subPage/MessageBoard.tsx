import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { githubIssuesApi } from '@/api'
import type { MessageBoardIssue } from '@/api'
import { MessageBoardMarkdownRenderer } from '@/features/messageBoard/markdownRenderer'

type LoadState = 'idle' | 'loading' | 'success' | 'error'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
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
    return '未找到 GitHub 仓库或 Issues 未开放。'
  }

  return '暂时无法连接 GitHub，请稍后重试。'
}

export default function MessageBoard() {
  const navigate = useNavigate()
  const [issues, setIssues] = useState<MessageBoardIssue[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const loadIssues = useCallback(async () => {
    setLoadState('loading')
    setErrorMessage('')

    try {
      const nextIssues = await githubIssuesApi.list()
      setIssues(nextIssues)
      setLoadState('success')
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
      setLoadState('error')
    }
  }, [])

  useEffect(() => {
    void loadIssues()
  }, [loadIssues])

  return (
    <main className="h-full overflow-auto bg-black px-4 py-5 text-zinc-100 sm:px-6">
      <section className="mx-auto flex max-w-4xl flex-col gap-4">
        <header className="border-b border-zinc-800 pb-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-white">留言板</h1>
            </div>
            <button
              className="w-fit rounded border border-zinc-700 px-3 py-1.5 text-sm text-zinc-200 transition hover:border-zinc-500 hover:bg-zinc-900"
              type="button"
              onClick={loadIssues}
              disabled={loadState === 'loading'}
            >
              {loadState === 'loading' ? '刷新中' : '刷新'}
            </button>
          </div>
        </header>

        {loadState === 'loading' && (
          <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            正在从 GitHub 加载留言...
          </div>
        )}

        {loadState === 'error' && (
          <div className="rounded border border-red-900/70 bg-red-950/30 px-4 py-5">
            <p className="text-sm text-red-100">{errorMessage}</p>
            <button
              className="mt-4 rounded border border-red-800 px-3 py-1.5 text-sm text-red-100 transition hover:bg-red-950"
              type="button"
              onClick={loadIssues}
            >
              重试
            </button>
          </div>
        )}

        {loadState === 'success' && issues.length === 0 && (
          <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            目前还没有留言。
          </div>
        )}

        {loadState === 'success' && issues.length > 0 && (
          <div className="flex flex-col gap-3">
            {issues.map((issue) => (
              <article
                className="cursor-pointer rounded border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900/80"
                key={issue.id}
                onClick={() => navigate(`/board/${issue.number}`)}
              >
                <div className="flex gap-3">
                  <img
                    className="h-10 w-10 shrink-0 rounded object-cover"
                    src={issue.author.avatarUrl}
                    alt={`${issue.author.login} avatar`}
                    loading="lazy"
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <a
                        className="min-w-0 flex-1 text-base font-semibold text-white underline-offset-2 hover:text-sky-200 hover:underline"
                        href={issue.htmlUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(event) => event.stopPropagation()}
                      >
                        {issue.title}
                      </a>
                      <span
                        className={`rounded px-2 py-0.5 text-xs ${
                          issue.state === 'open'
                            ? 'bg-emerald-950 text-emerald-200'
                            : 'bg-zinc-800 text-zinc-300'
                        }`}
                      >
                        {issue.state}
                      </span>
                    </div>

                    <p className="mt-1 text-xs text-zinc-500">
                      #{issue.number} by {issue.author.login} · 更新于 {formatDate(issue.updatedAt)} ·{' '}
                      {issue.commentsCount} 条评论
                    </p>

                    {issue.body ? (
                      <div className="mt-3 line-clamp-3 text-sm leading-6 text-zinc-300">
                        <MessageBoardMarkdownRenderer markdown={issue.body} />
                      </div>
                    ) : (
                      <p className="mt-3 text-sm text-zinc-500">这个 issue 没有正文。</p>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}
