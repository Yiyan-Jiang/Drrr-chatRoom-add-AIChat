export interface NewsHeading {
  id: string
  level: 2 | 3
  text: string
}

export interface NewsFrontmatter {
  title: string
  date: string
  author?: string
  category?: string
  tags?: string[]
}

export interface ParsedNewsMarkdown {
  frontmatter: NewsFrontmatter
  excerpt: string
  body: string
  headings: NewsHeading[]
}

export interface NewsDocument extends ParsedNewsMarkdown {
  slug: string
  author: string
  category: string | null
  tags: string[]
  title: string
  date: string
}

export interface AdjacentNewsDocuments {
  previous: NewsDocument | null
  next: NewsDocument | null
}
