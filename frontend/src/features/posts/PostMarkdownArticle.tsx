/** 渲染帖子 Markdown 正文及代码块。 */
import type { Components } from 'react-markdown'
import { MarkdownRenderer } from '@/features/news/markdownRenderer'

/** 帖子文章正文组件的输入属性。 */
type PostMarkdownArticleProps = {
  /** 待渲染的 Markdown 源文本。 */
  markdown: string
}

/**
 * 使用共享文章渲染器显示帖子正文，并覆盖二级和三级标题样式。
 * @param props - 帖子 Markdown 正文。
 * @returns 帖子文章正文组件。
 */
export default function PostMarkdownArticle({
  markdown,
}: PostMarkdownArticleProps) {
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
