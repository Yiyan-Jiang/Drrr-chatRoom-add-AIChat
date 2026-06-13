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

export const prettyCodeSelectors = {
  line: '[data-line]',
  highlightedLine: '[data-highlighted-line]',
  highlightedChars: '[data-highlighted-chars]',
} as const

const prettyCodeOptions = {
  theme: 'github-light',
  keepBackground: false,
} as const

type MarkdownRendererProps = {
  markdown: string
  components?: Components
  headingIds?: string[]
}

type HastNode = {
  type?: string
  tagName?: string
  properties?: Record<string, unknown>
  children?: HastNode[]
}

function applyHeadingIds(headingIds: string[]) {
  return function transform(tree: HastNode) {
    let headingIndex = 0

    function visit(node: HastNode) {
      if (
        node.type === 'element'
        && (node.tagName === 'h2' || node.tagName === 'h3')
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

function renderInlineCode(children: ReactNode) {
  return (
    <code className="inline-code rounded bg-[#f6f6f7] px-1.5 py-0.5 text-[13px] font-semibold text-[#213547]">
      {children}
    </code>
  )
}

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

  if (isValidElement<{ children?: ReactNode }>(node)) {
    return getTextContent(node.props.children)
  }

  return ''
}

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

type CodeBlockPreProps = HTMLAttributes<HTMLPreElement> & {
  node?: unknown
}

function CodeBlockPre({ children, node: _node, ...props }: CodeBlockPreProps) {
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
  a: ({ children, href }) => (
    <a
      className="font-medium text-[#3451b2] underline-offset-2 hover:underline"
      href={href}
      target={href?.startsWith('#') ? undefined : '_blank'}
      rel={href?.startsWith('#') ? undefined : 'noopener noreferrer'}
    >
      {children}
    </a>
  ),
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
    const isBlock = Boolean(className?.includes('language-'))
      || Boolean((props as { 'data-language'?: string })['data-language'])

    return isBlock
      ? <code className="block text-[#213547]">{children}</code>
      : renderInlineCode(children)
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
  hr: () => <hr className="border-[#e2e2e3]" />,
}

export function MarkdownRenderer({ markdown, components, headingIds }: MarkdownRendererProps) {
  const mergedComponents = {
    ...defaultComponents,
    ...components,
  } satisfies Components
  const rehypePlugins: PluggableList = headingIds
    ? [[applyHeadingIds, headingIds], [rehypePrettyCode, prettyCodeOptions]]
    : [[rehypePrettyCode, prettyCodeOptions]]

  return (
    <MarkdownHooks
      remarkPlugins={[remarkGfm]}
      rehypePlugins={rehypePlugins}
      components={mergedComponents}
      fallback={<div className="text-[15px] leading-7 text-[#3c3c43]">Loading...</div>}
    >
      {markdown}
    </MarkdownHooks>
  )
}

export type SupportedHighlightLanguage = BundledLanguage
