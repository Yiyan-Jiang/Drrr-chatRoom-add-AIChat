import { MarkdownHooks } from 'react-markdown'
import rehypePrettyCode from 'rehype-pretty-code'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'

type PostsMarkdownRendererProps = {
  markdown: string
  preview?: boolean
}

const prettyCodeOptions = {
  theme: 'github-dark',
  keepBackground: false,
} as const

const SAFE_URL_PROTOCOLS = new Set(['http:', 'https:', 'mailto:'])

function sanitizeUrl(url: string | undefined): string | undefined {
  if (!url) {
    return undefined
  }

  const trimmed = url.trim()
  if (
    trimmed.startsWith('#')
    || trimmed.startsWith('/')
    || trimmed.startsWith('./')
    || trimmed.startsWith('../')
  ) {
    return trimmed
  }

  try {
    const parsed = new URL(trimmed, window.location.origin)
    if (SAFE_URL_PROTOCOLS.has(parsed.protocol)) {
      return trimmed
    }
  } catch {
    // Unsafe or malformed URLs are dropped.
  }

  return undefined
}

function createComponents(preview: boolean): Components {
  return {
    a: ({ children, href }) => {
      const safeHref = sanitizeUrl(href)
      const isAnchor = safeHref?.startsWith('#')
      return (
        <a
          className="font-medium text-sky-300 underline-offset-2 hover:text-sky-200 hover:underline"
          href={safeHref}
          target={isAnchor ? undefined : '_blank'}
          rel={isAnchor ? undefined : 'noopener noreferrer'}
        >
          {children}
        </a>
      )
    },
    p: ({ children }) => (
      <p className="text-sm leading-6 text-zinc-300">{children}</p>
    ),
    h1: ({ children }) => (
      <h1 className="text-lg font-semibold leading-7 text-zinc-100">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-base font-semibold leading-6 text-zinc-100">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-sm font-semibold leading-6 text-zinc-100">{children}</h3>
    ),
    ul: ({ children }) => (
      <ul className="list-disc space-y-1 pl-5 text-sm leading-6 text-zinc-300">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal space-y-1 pl-5 text-sm leading-6 text-zinc-300">
        {children}
      </ol>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-zinc-700 pl-3 text-sm text-zinc-400">
        {children}
      </blockquote>
    ),
    code: ({ children, className, ...props }) => {
      const isBlock = Boolean(className?.includes('language-'))
        || Boolean((props as { 'data-language'?: string })['data-language'])
      return isBlock ? (
        <code className="block text-zinc-200">{children}</code>
      ) : (
        <code className="rounded bg-zinc-800 px-1.5 py-0.5 text-[13px] font-semibold text-zinc-100">
          {children}
        </code>
      )
    },
    pre: ({ children, ...props }) => (
      <pre
        {...props}
        className="max-w-full overflow-auto rounded border border-zinc-800 bg-zinc-950 p-3 text-sm leading-6 text-zinc-200"
      >
        {children}
      </pre>
    ),
    img: ({ src, alt }) => {
      const safeSrc = sanitizeUrl(typeof src === 'string' ? src : undefined)
      if (!safeSrc) {
        return <>{alt}</>
      }
      if (preview) {
        return <span className="text-zinc-500">[图片]</span>
      }
      return (
        <img
          className="max-h-80 max-w-full rounded border border-zinc-800 object-contain"
          src={safeSrc}
          alt={alt}
          loading="lazy"
        />
      )
    },
    table: ({ children }) => (
      <div className="overflow-auto rounded border border-zinc-800">
        <table className="w-full border-collapse text-sm text-zinc-300">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border border-zinc-800 bg-zinc-900 px-3 py-2 text-left font-semibold text-zinc-100">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="border border-zinc-800 px-3 py-2">{children}</td>
    ),
    hr: () => <hr className="border-zinc-800" />,
  }
}

export function PostsMarkdownRenderer({ markdown, preview = false }: PostsMarkdownRendererProps) {
  return (
    <MarkdownHooks
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[[rehypePrettyCode, prettyCodeOptions]]}
      components={createComponents(preview)}
      fallback={<div className="text-sm leading-6 text-zinc-300">Loading...</div>}
    >
      {markdown}
    </MarkdownHooks>
  )
}
