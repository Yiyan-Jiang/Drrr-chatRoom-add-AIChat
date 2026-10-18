/** 解析动态文章元信息、正文与目录，并构建文章列表。 */
import type {
  AdjacentNewsDocuments,
  NewsDocument,
  NewsFrontmatter,
  NewsHeading,
  ParsedNewsMarkdown,
} from './newsTypes.js'

const frontmatterPattern = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/
const moreMarkerPattern = /\r?\n?<!--\s*more\s*-->\r?\n?/i
const headingPattern = /^(#{2,3})\s+(.+)$/gm

/**
 * 清理标题标记并将非字母数字段替换为连字符，生成锚点基础编号。
 * @param value - 标题文本。
 * @returns 小写锚点编号；无有效字符时为 section。
 */
export function slugifyHeading(value: string): string {
  const slug = value
    .trim()
    .toLowerCase()
    .replace(/[`*_~[\]()]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')

  return slug || 'section'
}

/**
 * 去除标题中的 HTML 和常见 Markdown 标记，并压缩空白。
 * @param value - 原始标题文本。
 * @returns 用于目录显示与锚点生成的文本。
 */
export function normalizeHeadingText(value: string): string {
  return value
    .replace(/<[^>]*>/g, '')
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(\*|_)(.*?)\1/g, '$2')
    .replace(/~~(.*?)~~/g, '$1')
    .replace(/\s+/g, ' ')
    .trim()
}

/**
 * 解析文章顶部元信息、摘要分隔符和二三级标题。
 * @param markdown - 完整 Markdown 文件内容。
 * @returns 元信息、摘要、正文和目录。
 */
export function parseNewsMarkdown(markdown: string): ParsedNewsMarkdown {
  const match = markdown.match(frontmatterPattern)
  const frontmatter = parseFrontmatter(match?.[1] ?? '')
  const content = match
    ? markdown.slice(match[0].length).trim()
    : markdown.trim()
  const [excerpt, body] = splitExcerptAndBody(content)

  return {
    frontmatter,
    excerpt,
    body,
    headings: extractHeadings(body),
  }
}

/**
 * 将文件路径与 Markdown 内容组合为文章文档。
 * @param path - 用于提取文章路由标识的文件路径。
 * @param markdown - 完整 Markdown 文件内容。
 * @returns 含有路由标识和展示元信息的文章文档。
 */
export function buildNewsDocument(
  path: string,
  markdown: string,
): NewsDocument {
  const parsed = parseNewsMarkdown(markdown)

  return {
    ...parsed,
    slug: pathToSlug(path),
    title: parsed.frontmatter.title,
    date: parsed.frontmatter.date,
    author: parsed.frontmatter.author || 'Unknown',
    category: parsed.frontmatter.category || null,
    tags: parsed.frontmatter.tags ?? [],
  }
}

/**
 * 构建全部文章，并按日期倒序、同日按路由标识排序。
 * @param files - 文件路径到 Markdown 源文的映射。
 * @returns 排序后的文章数组。
 */
export function buildNewsDocuments(
  files: Record<string, string>,
): NewsDocument[] {
  return Object.entries(files)
    .map(([path, markdown]) => buildNewsDocument(path, markdown))
    .sort((left, right) => {
      const byDate = Date.parse(right.date) - Date.parse(left.date)
      return byDate || left.slug.localeCompare(right.slug)
    })
}

/**
 * 按路由标识从现有文章数组中查找文档。
 * @param documents - 已构建的文章集合。
 * @param slug - 文章路由标识。
 * @returns 匹配文档；未提供标识或无匹配时为 null。
 */
export function getNewsDocumentBySlug(
  documents: NewsDocument[],
  slug: string | undefined,
): NewsDocument | null {
  if (!slug) {
    return null
  }

  return documents.find((document) => document.slug === slug) ?? null
}

/**
 * 按输入数组顺序查询指定文章的相邻文章。
 * @param documents - 已排序的文章数组。
 * @param slug - 当前文章路由标识。
 * @returns 前一项和后一项；当前文章不存在时两项均为 null。
 */
export function getAdjacentNewsDocuments(
  documents: NewsDocument[],
  slug: string,
): AdjacentNewsDocuments {
  const index = documents.findIndex((document) => document.slug === slug)

  if (index < 0) {
    return { previous: null, next: null }
  }

  return {
    previous: documents[index - 1] ?? null,
    next: documents[index + 1] ?? null,
  }
}

/**
 * 提取非空文章分类，去重后按本地化比较顺序排序。
 * @param documents - 待提取分类的文章集合。
 * @returns 唯一分类名称数组。
 */
export function getNewsCategories(documents: NewsDocument[]): string[] {
  return Array.from(
    new Set(
      documents
        .map((document) => document.category)
        .filter((category): category is string => Boolean(category)),
    ),
  ).sort((left, right) => left.localeCompare(right))
}

/**
 * 同时按分类和不区分大小写的文本查询筛选文章。
 * @param documents - 待筛选文章。
 * @param filters - 查询文本与分类；all 表示全部分类。
 * @returns 保留输入顺序的匹配文章数组。
 */
export function filterNewsDocuments(
  documents: NewsDocument[],
  filters: {
    /** 在标题、摘要、正文、作者、分类和标签中匹配的查询文本。 */ query: string
    /** 需要保留的文章分类；all 表示不过滤分类。 */ category: string
  },
): NewsDocument[] {
  const query = filters.query.trim().toLowerCase()

  return documents.filter((document) => {
    const matchesCategory =
      filters.category === 'all' || document.category === filters.category

    if (!matchesCategory) {
      return false
    }

    if (!query) {
      return true
    }

    const searchableText = [
      document.title,
      document.excerpt,
      document.body,
      document.author,
      document.category ?? '',
      ...document.tags,
    ]
      .join(' ')
      .toLowerCase()

    return searchableText.includes(query)
  })
}

/**
 * 按每行第一个冒号拆分元信息；标题和日期缺失时使用当前约定的默认文本。
 * @param source - 不包含上下分隔线的顶部元信息文本。
 * @returns 标题、日期、作者、分类和逗号分隔标签。
 */
function parseFrontmatter(source: string): NewsFrontmatter {
  const fields = new Map<string, string>()

  for (const line of source.split(/\r?\n/)) {
    const separatorIndex = line.indexOf(':')

    if (separatorIndex <= 0) {
      continue
    }

    const key = line.slice(0, separatorIndex).trim()
    const value = line.slice(separatorIndex + 1).trim()
    fields.set(key, value)
  }

  return {
    title: fields.get('title') || 'Untitled',
    date: fields.get('date') || '',
    author: fields.get('author'),
    category: fields.get('category'),
    tags: parseTags(fields.get('tags')),
  }
}

/**
 * 按逗号拆分文章标签，去除首尾空白并过滤空项。
 * @param value - 顶部元信息中的 tags 文本。
 * @returns 标签数组；未提供文本时为空数组。
 */
function parseTags(value: string | undefined): string[] {
  if (!value) {
    return []
  }

  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

/**
 * 以 more 标记前的内容作为摘要；没有标记时使用首段，正文保留摘要并移除标记。
 * @param content - 已移除顶部元信息的 Markdown 内容。
 * @returns 摘要和完整正文。
 */
function splitExcerptAndBody(content: string): [string, string] {
  const parts = content.split(moreMarkerPattern)

  if (parts.length > 1) {
    return [parts[0]?.trim() ?? '', parts.join('\n').trim()]
  }

  const firstParagraph = content.split(/\r?\n\s*\r?\n/)[0]?.trim() ?? ''
  return [firstParagraph, content]
}

/**
 * 按行匹配二级和三级标题，清理展示文本，并为重复锚点追加序号。
 * @param markdown - 文章 Markdown 正文。
 * @returns 按正文顺序排列的目录项。
 */
function extractHeadings(markdown: string): NewsHeading[] {
  const usedIds = new Map<string, number>()
  const headings: NewsHeading[] = []

  for (const match of markdown.matchAll(headingPattern)) {
    const level = match[1]?.length
    const rawText = match[2] ?? ''
    const text = normalizeHeadingText(rawText.replace(/\s+#+$/, ''))
    const baseId = slugifyHeading(text)
    const count = usedIds.get(baseId) ?? 0
    const id = count === 0 ? baseId : `${baseId}-${count + 1}`

    usedIds.set(baseId, count + 1)

    if (level === 2 || level === 3) {
      headings.push({ id, level, text })
    }
  }

  return headings
}

/**
 * 提取路径中的文件名并移除 .md 扩展名。
 * @param path - Markdown 文件路径。
 * @returns 用作文章路由的文件名标识。
 */
function pathToSlug(path: string): string {
  const fileName = path.split(/[\\/]/).pop() ?? path
  return fileName.replace(/\.md$/i, '')
}
