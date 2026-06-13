import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  filterNewsDocuments,
  getAllNewsDocuments,
  getNewsCategories,
} from '@/features/news/newsDocuments'
import type { NewsDocument } from '@/features/news/newsTypes'

const PAGE_SIZE = 10

function formatDate(value: string): string {
  if (!value) {
    return '未设置日期'
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

export default function NewsFeed() {
  const [documents, setDocuments] = useState<NewsDocument[]>([])
  const [loadState, setLoadState] = useState<'loading' | 'success' | 'error'>('loading')
  const [query, setQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const categories = getNewsCategories(documents)
  const filteredDocuments = filterNewsDocuments(documents, {
    query,
    category: selectedCategory,
  })
  const totalPages = Math.max(1, Math.ceil(filteredDocuments.length / PAGE_SIZE))
  const pageStart = (currentPage - 1) * PAGE_SIZE
  const paginatedDocuments = filteredDocuments.slice(pageStart, pageStart + PAGE_SIZE)

  useEffect(() => {
    let isCurrent = true

    setLoadState('loading')
    getAllNewsDocuments().then(
      (nextDocuments) => {
        if (!isCurrent) {
          return
        }

        setDocuments(nextDocuments)
        setLoadState('success')
      },
      () => {
        if (isCurrent) {
          setLoadState('error')
        }
      },
    )

    return () => {
      isCurrent = false
    }
  }, [])

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages)
    }
  }, [currentPage, totalPages])

  return (
    <main className="h-full overflow-auto bg-black px-4 py-5 text-zinc-100 sm:px-6">
      <section className="mx-auto flex max-w-4xl flex-col gap-4">
        <header className="border-b border-zinc-800 pb-4">
          <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
            Static Docs
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-white">新闻流</h1>
          <p className="mt-2 text-sm leading-6 text-zinc-400">
            公告、更新记录和技术说明会以 Markdown 静态文档的形式展示。
          </p>
        </header>

        <section className="flex flex-col gap-3 border-b border-zinc-900 pb-4">
          <label className="flex flex-col gap-2 text-sm text-zinc-400">
            <span>搜索新闻</span>
            <input
              className="rounded border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none transition placeholder:text-zinc-600 focus:border-zinc-500"
              onChange={(event) => {
                setQuery(event.target.value)
                setCurrentPage(1)
              }}
              placeholder="搜索标题、摘要、正文或标签"
              type="search"
              value={query}
            />
          </label>

          <div className="flex flex-wrap items-center gap-2">
            <button
              className={`rounded border px-3 py-1.5 text-sm transition ${
                selectedCategory === 'all'
                  ? 'border-sky-500 bg-sky-950/40 text-sky-100'
                  : 'border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-100'
              }`}
              onClick={() => {
                setSelectedCategory('all')
                setCurrentPage(1)
              }}
              type="button"
            >
              全部
            </button>
            {categories.map((category) => (
              <button
                className={`rounded border px-3 py-1.5 text-sm transition ${
                  selectedCategory === category
                    ? 'border-sky-500 bg-sky-950/40 text-sky-100'
                    : 'border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-100'
                }`}
                key={category}
                onClick={() => {
                  setSelectedCategory(category)
                  setCurrentPage(1)
                }}
                type="button"
              >
                {category}
              </button>
            ))}
            <span className="ml-auto text-xs text-zinc-500">
              {filteredDocuments.length} / {documents.length}
            </span>
          </div>
        </section>

        {loadState === 'loading' ? (
          <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            正在加载新闻文档...
          </div>
        ) : loadState === 'error' ? (
          <div className="rounded border border-red-900/70 bg-red-950/30 px-4 py-5 text-sm text-red-100">
            无法加载新闻文档。
          </div>
        ) : documents.length === 0 ? (
          <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            暂时还没有新闻文档。
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            没有找到匹配的新闻文档。
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {paginatedDocuments.map((document) => (
              <Link
                className="group block rounded border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900/80"
                key={document.slug}
                to={`/news/${document.slug}`}
              >
                <div className="flex flex-col gap-3">
                  <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                    <span>{formatDate(document.date)}</span>
                    <span>by {document.author}</span>
                    {document.category && (
                      <span className="rounded bg-zinc-900 px-2 py-0.5 text-zinc-300">
                        {document.category}
                      </span>
                    )}
                  </div>

                  <div>
                    <h2 className="text-lg font-semibold text-white">
                      <span className="underline-offset-2 transition group-hover:text-sky-200 group-hover:underline">
                        {document.title}
                      </span>
                    </h2>
                    <p className="mt-2 text-sm leading-6 text-zinc-400">
                      {document.excerpt}
                    </p>
                  </div>

                  {document.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {document.tags.map((tag) => (
                        <span
                          className="rounded border border-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
                          key={tag}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            ))}
            {totalPages > 1 && (
              <nav
                aria-label="新闻分页"
                className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-900 pt-4 text-sm"
              >
                <button
                  className="rounded border border-zinc-800 px-3 py-1.5 text-zinc-300 transition hover:border-zinc-600 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-zinc-800 disabled:hover:text-zinc-300"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                  type="button"
                >
                  上一页
                </button>
                <span className="text-xs text-zinc-500">
                  第 {currentPage} / {totalPages} 页
                </span>
                <button
                  className="rounded border border-zinc-800 px-3 py-1.5 text-zinc-300 transition hover:border-zinc-600 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-zinc-800 disabled:hover:text-zinc-300"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                  type="button"
                >
                  下一页
                </button>
              </nav>
            )}
          </div>
        )}
      </section>
    </main>
  )
}
