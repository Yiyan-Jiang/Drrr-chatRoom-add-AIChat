/** 加载构建时发现的动态文章 Markdown 文件。 */
import {
  buildNewsDocument,
  buildNewsDocuments,
  filterNewsDocuments,
  getAdjacentNewsDocuments,
  getNewsCategories,
} from './newsDocumentsCore.js'
import type { NewsDocument } from './newsTypes'

/** Markdown 动态导入可能返回的原始文本或默认导出。 */
type MarkdownModule =
  string | { /** 动态导入模块的 Markdown 源文本默认导出。 */ default: string }
/** 异步加载单个 Markdown 模块的函数。 */
type MarkdownLoader = () => Promise<MarkdownModule>

const markdownFiles = import.meta.glob('../../content/news/*.md', {
  import: 'default',
  query: '?raw',
}) as Record<string, MarkdownLoader>

let documentsCache: NewsDocument[] | null = null

/**
 * 并行加载全部动态文章，按日期排序后缓存结果。
 * @returns 缓存或首次构建的文章数组。
 */
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

/**
 * 按文件名匹配动态文章并单独加载。
 * @param slug - 不含 .md 扩展名的文章标识。
 * @returns 匹配文章；未提供标识或文件不存在时为 null。
 */
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

/**
 * 读取 Markdown 加载器结果，并兼容原始文本和默认导出两种模块形状。
 * @param load - 单篇文章的异步加载器。
 * @returns Markdown 源文本。
 */
async function loadMarkdown(load: MarkdownLoader): Promise<string> {
  const module = await load()
  return typeof module === 'string' ? module : module.default
}

export { filterNewsDocuments, getAdjacentNewsDocuments, getNewsCategories }
