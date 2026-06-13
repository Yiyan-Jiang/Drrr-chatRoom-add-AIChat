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

export function slugifyHeading(value: string): string {
  const slug = value
    .trim()
    .toLowerCase()
    .replace(/[`*_~[\]()]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')

  return slug || 'section'
}

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

export function parseNewsMarkdown(markdown: string): ParsedNewsMarkdown {
  const match = markdown.match(frontmatterPattern)
  const frontmatter = parseFrontmatter(match?.[1] ?? '')
  const content = match ? markdown.slice(match[0].length).trim() : markdown.trim()
  const [excerpt, body] = splitExcerptAndBody(content)

  return {
    frontmatter,
    excerpt,
    body,
    headings: extractHeadings(body),
  }
}

export function buildNewsDocument(path: string, markdown: string): NewsDocument {
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

export function buildNewsDocuments(files: Record<string, string>): NewsDocument[] {
  return Object.entries(files)
    .map(([path, markdown]) => buildNewsDocument(path, markdown))
    .sort((left, right) => {
      const byDate = Date.parse(right.date) - Date.parse(left.date)
      return byDate || left.slug.localeCompare(right.slug)
    })
}

export function getNewsDocumentBySlug(
  documents: NewsDocument[],
  slug: string | undefined,
): NewsDocument | null {
  if (!slug) {
    return null
  }

  return documents.find((document) => document.slug === slug) ?? null
}

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

export function getNewsCategories(documents: NewsDocument[]): string[] {
  return Array.from(
    new Set(
      documents
        .map((document) => document.category)
        .filter((category): category is string => Boolean(category)),
    ),
  ).sort((left, right) => left.localeCompare(right))
}

export function filterNewsDocuments(
  documents: NewsDocument[],
  filters: { query: string; category: string },
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
    ].join(' ').toLowerCase()

    return searchableText.includes(query)
  })
}

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

function parseTags(value: string | undefined): string[] {
  if (!value) {
    return []
  }

  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function splitExcerptAndBody(content: string): [string, string] {
  const parts = content.split(moreMarkerPattern)

  if (parts.length > 1) {
    return [parts[0]?.trim() ?? '', parts.join('\n').trim()]
  }

  const firstParagraph = content.split(/\r?\n\s*\r?\n/)[0]?.trim() ?? ''
  return [firstParagraph, content]
}

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

function pathToSlug(path: string): string {
  const fileName = path.split(/[\\/]/).pop() ?? path
  return fileName.replace(/\.md$/i, '')
}
