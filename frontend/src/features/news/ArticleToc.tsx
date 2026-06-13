import type { NewsHeading } from './newsTypes'

interface ArticleTocProps {
  headings: NewsHeading[]
  onNavigate?: () => void
}

export default function ArticleToc({ headings, onNavigate }: ArticleTocProps) {
  if (headings.length === 0) {
    return null
  }

  return (
    <nav className="flex max-h-[calc(100vh-5rem)] flex-col overflow-hidden rounded-lg border border-[#e2e2e3] bg-[#ffffff] p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#67676c]">
        Contents
      </p>
      <div className="article-toc-scrollbar mt-3 flex min-h-0 flex-col gap-2 overflow-y-auto pr-1">
        {headings.map((heading) => (
          <a
            className={`flex min-h-9 min-w-0 items-center border-l border-transparent text-sm text-[#3c3c43] underline-offset-2 transition hover:border-[#3451b2] hover:text-[#3451b2] hover:underline ${
              heading.level === 3 ? 'pl-5' : 'pl-2'
            }`}
            href={`#${heading.id}`}
            key={heading.id}
            onClick={onNavigate}
            title={heading.text}
          >
            <span className="block min-w-0 truncate whitespace-nowrap leading-6">
              {heading.text}
            </span>
          </a>
        ))}
      </div>
    </nav>
  )
}
