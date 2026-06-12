import {
  buildNewsDocument,
  buildNewsDocuments,
  filterNewsDocuments,
  getAdjacentNewsDocuments,
  getNewsCategories,
} from './newsDocumentsCore.js'
import type { NewsDocument } from './newsTypes'

type MarkdownModule = string | { default: string }
type MarkdownLoader = () => Promise<MarkdownModule>

const markdownFiles = import.meta.glob('../../content/news/*.md', {
  import: 'default',
  query: '?raw',
}) as Record<string, MarkdownLoader>

let documentsCache: NewsDocument[] | null = null

export async function getAllNewsDocuments(): Promise<NewsDocument[]> {
  if (documentsCache) {
    return documentsCache
  }

  const entries = await Promise.all(
    Object.entries(markdownFiles).map(async ([path, load]) => {
      const markdown = await loadMarkdown(load)
      return [path, markdown] as const
    }),
  )

  documentsCache = buildNewsDocuments(Object.fromEntries(entries))
  return documentsCache
}

export async function getNewsDocumentBySlug(
  slug: string | undefined,
): Promise<NewsDocument | null> {
  if (!slug) {
    return null
  }

  const match = Object.entries(markdownFiles).find(([path]) => {
    const fileName = path.split(/[\\/]/).pop() ?? path
    return fileName.replace(/\.md$/i, '') === slug
  })

  if (!match) {
    return null
  }

  const [path, load] = match
  const markdown = await loadMarkdown(load)
  return buildNewsDocument(path, markdown)
}

async function loadMarkdown(load: MarkdownLoader): Promise<string> {
  const module = await load()
  return typeof module === 'string' ? module : module.default
}

export {
  filterNewsDocuments,
  getAdjacentNewsDocuments,
  getNewsCategories,
}
