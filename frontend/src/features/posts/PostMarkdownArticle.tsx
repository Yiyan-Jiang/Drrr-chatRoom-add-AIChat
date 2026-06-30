import type { Components } from 'react-markdown'
import { MarkdownRenderer } from '@/features/news/markdownRenderer'

type PostMarkdownArticleProps = {
  markdown: string
}

export default function PostMarkdownArticle({ markdown }: PostMarkdownArticleProps) {
  const components: Components = {
    h2: ({ children, id }) => (
      <h2
        className="group scroll-mt-20 border-t border-[#e2e2e3] pt-8 text-2xl font-semibold tracking-tight text-[#213547]"
        id={typeof id === 'string' ? id : undefined}
      >
        {children}
      </h2>
    ),
    h3: ({ children, id }) => (
      <h3
        className="group scroll-mt-20 pt-5 text-xl font-semibold tracking-tight text-[#213547]"
        id={typeof id === 'string' ? id : undefined}
      >
        {children}
      </h3>
    ),
  }

  return (
    <div className="vp-doc-like min-w-0 flex flex-col gap-5 text-[#213547]">
      <MarkdownRenderer markdown={markdown} components={components} />
    </div>
  )
}
