/** 为动态文章配置 Markdown、代码高亮及渲染组件。 */
import {
  isValidElement,
  useEffect,
  useState,
  type HTMLAttributes,
  type ReactNode,
} from 'react'
import { MarkdownHooks } from 'react-markdown'
import rehypePrettyCode from 'rehype-pretty-code'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'
import type { BundledLanguage } from 'shiki'
import type { PluggableList } from 'unified'

const prettyCodeOptions = {
  theme: 'github-light',
  keepBackground: false,
} as const

/** 共享 Markdown 渲染器的正文、组件覆盖和标题锚点配置。 */
type MarkdownRendererProps = {
  /** 待渲染的 Markdown 源文本。 */
  markdown: string
  /** 覆盖默认标签渲染方式的组件集合。 */
  components?: Components
  /** 按二级和三级标题出现顺序分配的锚点编号。 */
  headingIds?: string[]
}

/** 标题锚点转换所需的 HAST 节点子集。 */
type HastNode = {
  /** HAST 节点种类。 */
  type?: string
  /** 元素节点的 HTML 标签名。 */
  tagName?: string
  /** 元素节点属性。 */
  properties?: Record<string, unknown>
  /** 当前语法树节点的子节点。 */
  children?: HastNode[]
}

/**
 * 创建 rehype 插件，按二级和三级标题的出现顺序写入给定锚点。
 * @param headingIds - 与标题顺序对应的锚点编号。
 * @returns 会修改 HAST 标题属性的转换函数。
 */
function applyHeadingIds(headingIds: string[]) {
  return /** 遍历当前 HAST 树，为二级和三级标题写入对应的锚点属性。 */ function transform(
    tree: HastNode,
  ) {
    let headingIndex = 0

    /**
     * 深度遍历子节点，并为当前二级或三级标题分配下一项锚点。
     * @param node - 当前遍历到的 HAST 节点。
     */
    function visit(node: HastNode) {
      if (
        node.type === 'element' &&
        (node.tagName === 'h2' || node.tagName === 'h3')
      ) {
        const id = headingIds[headingIndex]
        headingIndex += 1

        if (id) {
          node.properties = {
            ...node.properties,
            id,
          }
        }
      }

      node.children?.forEach(visit)
    }

    visit(tree)
  }
}

const SAFE_URL_PROTOCOLS = new Set(['http:', 'https:', 'mailto:'])

/**
 * 允许页内锚点、相对地址以及 http、https 和 mailto 链接，其余地址返回 undefined。
 * @param url - Markdown 提供的链接或图片地址。
 * @returns 去除首尾空白的可用地址，或 undefined。
 */
function sanitizeUrl(url: string | undefined): string | undefined {
  if (!url) {
    return undefined
  }

  const trimmed = url.trim()

  // 允许页内锚点、相对链接和协议相对链接。
  if (
    trimmed.startsWith('#') ||
    trimmed.startsWith('/') ||
    trimmed.startsWith('./') ||
    trimmed.startsWith('../')
  ) {
    return trimmed
  }

  try {
    const parsed = new URL(trimmed, window.location.origin)
    if (SAFE_URL_PROTOCOLS.has(parsed.protocol)) {
      return trimmed
    }
  } catch {
    // 无法解析的 URL 不作为可用链接。
  }

  return undefined
}

/**
 * 将行内代码内容放入统一样式的 code 标签。
 * @param children - 行内代码的子内容。
 * @returns 行内代码元素。
 */
function renderInlineCode(children: ReactNode) {
  return (
    <code className="inline-code rounded bg-[#f6f6f7] px-1.5 py-0.5 text-[13px] font-semibold text-[#213547]">
      {children}
    </code>
  )
}

/**
 * 递归提取 React 子节点中的文本和数字，忽略空值及布尔值。
 * @param node - 代码块内的 React 内容。
 * @returns 按子节点顺序拼接的文本。
 */
function getTextContent(node: ReactNode): string {
  if (node === null || node === undefined || typeof node === 'boolean') {
    return ''
  }

  if (typeof node === 'string' || typeof node === 'number') {
    return String(node)
  }

  if (Array.isArray(node)) {
    return node.map(getTextContent).join('')
  }

  if (
    isValidElement<{
      /** 需要继续提取文本的 React 子内容。 */ children?: ReactNode
    }>(node)
  ) {
    return getTextContent(node.props.children)
  }

  return ''
}

/**
 * 优先调用 Clipboard API 写入文本，不可用时创建临时文本框并调用旧版 copy 命令。
 * @param text - 需要写入剪贴板的代码文本。
 * @returns 写入流程结束的 Promise；Clipboard API 的失败会继续抛出。
 */
async function copyTextToClipboard(text: string) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }

  const textarea = window.document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', 'true')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  window.document.body.appendChild(textarea)
  textarea.select()
  window.document.execCommand('copy')
  window.document.body.removeChild(textarea)
}

/** 代码块容器的 DOM 属性和 Markdown 节点数据。 */
type CodeBlockPreProps = HTMLAttributes<HTMLPreElement> & {
  /** Markdown 传入的语法树节点，不传给 DOM。 */
  node?: unknown
}

/**
 * 渲染带复制按钮的代码块，并在点击复制后短暂显示已复制状态。
 * @param props - pre 标签属性、代码内容及需要从 DOM 属性中排除的语法树节点。
 * @returns 带复制操作的代码块容器。
 */
function CodeBlockPre({ children, node: _node, ...props }: CodeBlockPreProps) {
  void _node // Markdown 语法树节点不是 DOM 属性。
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!copied) {
      return
    }

    const timeoutId = window.setTimeout(() => {
      setCopied(false)
    }, 1600)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [copied])

  const handleCopy = async () => {
    await copyTextToClipboard(getTextContent(children).replace(/\n$/, ''))
    setCopied(true)
  }

  return (
    <div className="group relative max-w-full">
      <button
        aria-label={copied ? 'Code copied' : 'Copy code'}
        className="absolute right-2 top-2 z-10 inline-flex h-8 w-8 items-center justify-center rounded border border-[#dcdfe6] bg-white/90 text-[#67676c] opacity-0 shadow-sm transition hover:border-[#3451b2] hover:text-[#3451b2] focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-[#a8b1ff] group-hover:opacity-100"
        onClick={handleCopy}
        title={copied ? 'Code copied' : 'Copy code'}
        type="button"
      >
        <span className="sr-only">{copied ? 'Code copied' : 'Copy code'}</span>
        {copied ? (
          <svg
            aria-hidden="true"
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="m20 6-11 11-5-5" />
          </svg>
        ) : (
          <svg
            aria-hidden="true"
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <rect height="14" rx="2" width="14" x="8" y="8" />
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
          </svg>
        )}
      </button>
      <pre
        {...props}
        className="max-w-full overflow-auto rounded-lg border border-[#e2e2e3] bg-[#f6f6f7] p-4 text-sm leading-6 text-[#213547]"
      >
        {children}
      </pre>
    </div>
  )
}

const defaultComponents: Components = {
  a: ({ children, href }) => {
    const safeHref = sanitizeUrl(href)
    const isAnchor = safeHref?.startsWith('#')

    return (
      <a
        className="font-medium text-[#3451b2] underline-offset-2 hover:underline"
        href={safeHref}
        target={isAnchor ? undefined : '_blank'}
        rel={isAnchor ? undefined : 'noopener noreferrer'}
      >
        {children}
      </a>
    )
  },
  p: ({ children }) => (
    <p className="text-[15px] leading-7 text-[#3c3c43]">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc space-y-2 pl-6 text-[15px] leading-7 text-[#3c3c43]">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal space-y-2 pl-6 text-[15px] leading-7 text-[#3c3c43]">
      {children}
    </ol>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-[#dcdfe6] pl-4 text-[15px] text-[#67676c]">
      {children}
    </blockquote>
  ),
  code: ({ children, className, node: _node, ...props }) => {
    void _node
    const isBlock =
      Boolean(className?.includes('language-')) ||
      Boolean(
        (
          props as {
            /** 代码高亮插件写入的代码块语言标识。 */ 'data-language'?: string
          }
        )['data-language'],
      )

    return isBlock ? (
      <code className="block text-[#213547]">{children}</code>
    ) : (
      renderInlineCode(children)
    )
  },
  pre: CodeBlockPre,
  table: ({ children }) => (
    <div className="overflow-auto rounded border border-[#e2e2e3]">
      <table className="w-full border-collapse text-sm text-[#3c3c43]">
        {children}
      </table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-[#e2e2e3] bg-[#f6f6f7] px-3 py-2 text-left font-semibold text-[#213547]">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-[#e2e2e3] px-3 py-2">{children}</td>
  ),
  img: ({ src, alt }) => {
    const safeSrc = sanitizeUrl(typeof src === 'string' ? src : undefined)
    if (!safeSrc) {
      return <>{alt}</>
    }

    return <img src={safeSrc} alt={alt} loading="lazy" />
  },
  hr: () => <hr className="border-[#e2e2e3]" />,
}

/**
 * 合并默认渲染组件与调用方覆盖，并按需向二级和三级标题分配锚点。
 * @param props - Markdown 正文、可选组件覆盖与标题锚点。
 * @returns 启用 GFM 和代码高亮的 Markdown 组件。
 */
export function MarkdownRenderer({
  markdown,
  components,
  headingIds,
}: MarkdownRendererProps) {
  const mergedComponents = {
    ...defaultComponents,
    ...components,
  } satisfies Components
  const rehypePlugins: PluggableList = headingIds
    ? [
        [applyHeadingIds, headingIds],
        [rehypePrettyCode, prettyCodeOptions],
      ]
    : [[rehypePrettyCode, prettyCodeOptions]]

  return (
    <MarkdownHooks
      remarkPlugins={[remarkGfm]}
      rehypePlugins={rehypePlugins}
      components={mergedComponents}
      fallback={
        <div className="text-[15px] leading-7 text-[#3c3c43]">Loading...</div>
      }
    >
      {markdown}
    </MarkdownHooks>
  )
}

/** Shiki 内置代码高亮语言名称。 */
export type SupportedHighlightLanguage = BundledLanguage
