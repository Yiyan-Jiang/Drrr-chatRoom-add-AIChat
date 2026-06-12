import { useEffect, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import ArticleToc from '@/features/news/ArticleToc'
import MarkdownArticle from '@/features/news/MarkdownArticle'
import { scrollToHeadingById } from '@/features/news/newsAnchor'
import {
  getAdjacentNewsDocuments,
  getAllNewsDocuments,
  getNewsDocumentBySlug,
} from '@/features/news/newsDocuments'
import type { AdjacentNewsDocuments, NewsDocument } from '@/features/news/newsTypes'
import logoSource from '@/assets/icon/Logo/logo.png'

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

export default function NewsArticleDetail() {
  const { slug } = useParams()
  const [document, setDocument] = useState<NewsDocument | null>(null)
  const [adjacent, setAdjacent] = useState<AdjacentNewsDocuments>({
    previous: null,
    next: null,
  })
  const [isMobileTocOpen, setIsMobileTocOpen] = useState(false)
  const [loadState, setLoadState] = useState<'loading' | 'success' | 'not-found' | 'error'>('loading')

  useEffect(() => {
    let isCurrent = true

    setIsMobileTocOpen(false)
    setLoadState('loading')
    setDocument(null)
    setAdjacent({ previous: null, next: null })

    getNewsDocumentBySlug(slug).then(
      (nextDocument) => {
        if (!isCurrent) {
          return
        }

        if (!nextDocument) {
          setLoadState('not-found')
          return
        }

        setDocument(nextDocument)
        setLoadState('success')

        getAllNewsDocuments().then((documents) => {
          if (isCurrent) {
            setAdjacent(getAdjacentNewsDocuments(documents, nextDocument.slug))
          }
        })
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
  }, [slug])

  useEffect(() => {
    if (!isMobileTocOpen) {
      return
    }

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsMobileTocOpen(false)
      }
    }

    window.addEventListener('keydown', closeOnEscape)

    return () => {
      window.removeEventListener('keydown', closeOnEscape)
    }
  }, [isMobileTocOpen])

  useEffect(() => {
    if (loadState !== 'success') {
      return
    }

    const hash = window.location.hash

    if (!hash) {
      return
    }

    scrollToHeadingById(decodeURIComponent(hash.slice(1)), {
      updateHash: false,
    })
  }, [loadState, document?.slug])

  useEffect(() => {
    if (loadState !== 'success' || !document || document.headings.length === 0) {
      return
    }

    if (!('IntersectionObserver' in window)) {
      return
    }

    const headingIds = document.headings.map((heading) => heading.id)
    let observer: IntersectionObserver | null = null
    let frameId = 0
    let remainingAttempts = 12

    const getCurrentHash = () => {
      try {
        return decodeURIComponent(window.location.hash.slice(1))
      } catch {
        return window.location.hash.slice(1)
      }
    }

    const updateHash = (id: string) => {
      if (getCurrentHash() === id) {
        return
      }

      window.history.replaceState(null, '', `#${encodeURIComponent(id)}`)
    }

    const getHeadingElements = () => (
      headingIds
        .map((id) => window.document.getElementById(id))
        .filter((heading): heading is HTMLElement => Boolean(heading))
    )

    const updateActiveHeading = () => {
      const activeHeading = getHeadingElements()
        .reverse()
        .find((heading) => heading.getBoundingClientRect().top <= 96)

      if (activeHeading?.id) {
        updateHash(activeHeading.id)
      }
    }

    const setupObserver = () => {
      const headingElements = getHeadingElements()

      if (headingElements.length === 0 && remainingAttempts > 0) {
        remainingAttempts -= 1
        frameId = window.requestAnimationFrame(setupObserver)
        return
      }

      if (headingElements.length === 0) {
        return
      }

      observer = new IntersectionObserver(updateActiveHeading, {
        rootMargin: '-96px 0px -75% 0px',
      })

      headingElements.forEach((heading) => observer?.observe(heading))
      updateActiveHeading()
    }

    frameId = window.requestAnimationFrame(setupObserver)

    return () => {
      window.cancelAnimationFrame(frameId)
      if (observer) {
        observer.disconnect()
      }
    }
  }, [loadState, document])

  const shell = (children: ReactNode) => (
    <main className="min-h-screen bg-[#f6f6f7] pt-14 text-[#213547]">
      <header className="fixed inset-x-0 top-0 z-40 border-b border-zinc-900 bg-black/95">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link className="flex min-w-0 items-center gap-3" to="/home/news">
            <img
              alt="Drrr logo"
              className="h-8 w-8 shrink-0 object-contain"
              src={logoSource}
            />
            <span className="truncate text-sm font-semibold text-zinc-100">
              News Docs
            </span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            {document && document.headings.length > 0 && (
              <button
                aria-label="Open article contents"
                className="inline-flex h-9 w-9 items-center justify-center rounded border border-zinc-700 text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100 lg:hidden"
                onClick={() => setIsMobileTocOpen(true)}
                type="button"
              >
                <span className="sr-only">Contents</span>
                <span aria-hidden="true" className="flex flex-col gap-1">
                  <span className="block h-0.5 w-4 rounded bg-current" />
                  <span className="block h-0.5 w-4 rounded bg-current" />
                  <span className="block h-0.5 w-4 rounded bg-current" />
                </span>
              </button>
            )}
            <Link
              className="text-zinc-400 transition hover:text-zinc-100"
              to="/home/news"
            >
              新闻流
            </Link>
            <Link
              className="text-zinc-400 transition hover:text-zinc-100"
              to="/home/rooms"
            >
              聊天室
            </Link>
          </nav>
        </div>
      </header>
      {document && document.headings.length > 0 && isMobileTocOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            aria-label="Close article contents"
            className="absolute inset-0 bg-black/30"
            onClick={() => setIsMobileTocOpen(false)}
            type="button"
          />
          <div className="absolute right-4 top-16 w-[min(20rem,calc(100vw-2rem))] shadow-xl">
            <ArticleToc
              headings={document.headings}
              onNavigate={() => setIsMobileTocOpen(false)}
            />
          </div>
        </div>
      )}
      {children}
    </main>
  )

  if (loadState === 'loading') {
    return (
      shell(
        <section className="mx-auto flex max-w-4xl flex-col gap-4">
          <div className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] px-4 py-8 text-center text-sm text-[#67676c]">
            正在加载新闻文档...
          </div>
        </section>,
      )
    )
  }

  if (loadState === 'error') {
    return (
      shell(
        <section className="mx-auto flex max-w-4xl flex-col gap-4">
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-5 text-sm text-red-700">
            无法加载新闻文档。
          </div>
        </section>,
      )
    )
  }

  if (!document) {
    return (
      shell(
        <section className="mx-auto flex max-w-4xl flex-col gap-4">
          <div className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] px-4 py-8 text-center text-sm text-[#67676c]">
            没有找到这篇新闻文档。
          </div>
        </section>,
      )
    )
  }

  return (
    shell(
      <section className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-5 sm:px-6">
        <Link
          className="w-fit text-sm font-medium text-[#3451b2] transition hover:text-[#213547]"
          to="/home/news"
        >
          返回新闻流
        </Link>

        <article className="rounded-xl border border-[#e2e2e3] bg-[#ffffff] px-5 py-6 shadow-sm sm:px-8">
          <header className="border-b border-[#e2e2e3] pb-6">
            <div className="flex flex-wrap items-center gap-2 text-xs text-[#67676c]">
              <span>{formatDate(document.date)}</span>
              <span>by {document.author}</span>
              {document.category && (
                <span className="rounded-full bg-[#f6f6f7] px-2 py-0.5 text-[#3c3c43]">
                  {document.category}
                </span>
              )}
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-[#213547]">
              {document.title}
            </h1>
            {document.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {document.tags.map((tag) => (
                  <span
                    className="rounded-full border border-[#e2e2e3] bg-[#f6f6f7] px-2 py-0.5 text-xs text-[#67676c]"
                    key={tag}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </header>

          <div className="mt-6 grid gap-8 lg:grid-cols-[minmax(0,1fr)_220px]">
            <MarkdownArticle document={document} />
            <aside className="hidden lg:sticky lg:top-5 lg:block lg:self-start">
              <ArticleToc headings={document.headings} />
            </aside>
          </div>
        </article>

        <nav className="grid gap-3 sm:grid-cols-2">
          {adjacent.previous ? (
            <Link
              className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] p-3 text-sm text-[#3c3c43] shadow-sm transition hover:border-[#3451b2] hover:text-[#3451b2]"
              to={`/news/${adjacent.previous.slug}`}
            >
              <span className="block text-xs text-[#67676c]">上一篇</span>
              {adjacent.previous.title}
            </Link>
          ) : (
            <div />
          )}

          {adjacent.next ? (
            <Link
              className="rounded-lg border border-[#e2e2e3] bg-[#ffffff] p-3 text-right text-sm text-[#3c3c43] shadow-sm transition hover:border-[#3451b2] hover:text-[#3451b2]"
              to={`/news/${adjacent.next.slug}`}
            >
              <span className="block text-xs text-[#67676c]">下一篇</span>
              {adjacent.next.title}
            </Link>
          ) : (
            <div />
          )}
        </nav>
      </section>,
    )
  )
}
