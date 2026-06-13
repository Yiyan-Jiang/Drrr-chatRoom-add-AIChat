import type { Components } from 'react-markdown'
import { MarkdownRenderer } from './markdownRenderer'
import type { NewsDocument } from './newsTypes'

interface MarkdownArticleProps {
  document: NewsDocument
}

export default function MarkdownArticle({ document }: MarkdownArticleProps) {
  const components: Components = {
    h2: ({ children, id }) => {
      const heading = { id: typeof id === 'string' ? id : undefined }

      return (
        <h2
          className="group scroll-mt-20 border-t border-[#e2e2e3] pt-8 text-2xl font-semibold tracking-tight text-[#213547]"
          id={heading?.id}
        >
          {children}
          {heading?.id && (
            <a
              aria-label="Copy heading link"
              className="ml-2 text-[#a8b1ff] opacity-0 transition group-hover:opacity-100 hover:text-[#3451b2]"
              href={`#${heading?.id}`}
            >
              #
            </a>
          )}
        </h2>
      )
    },
    h3: ({ children, id }) => {
      const heading = { id: typeof id === 'string' ? id : undefined }

      return (
        <h3
          className="group scroll-mt-20 pt-5 text-xl font-semibold tracking-tight text-[#213547]"
          id={heading?.id}
        >
          {children}
          {heading?.id && (
            <a
              aria-label="Copy heading link"
              className="ml-2 text-[#a8b1ff] opacity-0 transition group-hover:opacity-100 hover:text-[#3451b2]"
              href={`#${heading?.id}`}
            >
              #
            </a>
          )}
        </h3>
      )
    },
  }

  return (
    <div className="vp-doc-like min-w-0 flex flex-col gap-5 text-[#213547]">
      <MarkdownRenderer
        markdown={document.body}
        components={components}
        headingIds={document.headings.map((heading) => heading.id)}
      />
    </div>
  )
}
