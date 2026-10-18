/** 定义动态文章的元信息、目录项和完整文档结构。 */
/** 从 Markdown 二级或三级标题提取的目录项。 */
export interface NewsHeading {
  /** 标题在正文中的锚点编号。 */
  id: string
  /** 目录标题级别，仅支持二级和三级。 */
  level: 2 | 3
  /** 去除 Markdown 标记后的标题文本。 */
  text: string
}

/** 动态文章顶部元信息区支持的字段。 */
export interface NewsFrontmatter {
  /** 文章标题。 */
  title: string
  /** 文章日期字符串。 */
  date: string
  /** 文章作者署名。 */
  author?: string
  /** 文章分类；无分类时可为空。 */
  category?: string
  /** 以逗号分隔的元信息解析得到的文章标签。 */
  tags?: string[]
}

/** 解析得到的文章元信息、摘要、正文和目录。 */
export interface ParsedNewsMarkdown {
  /** 解析后的文章元信息。 */
  frontmatter: NewsFrontmatter
  /** 用于列表展示的文章摘要。 */
  excerpt: string
  /** 移除顶部元信息和摘要分隔标记后的完整 Markdown 正文。 */
  body: string
  /** 按正文顺序排列的二级和三级标题。 */
  headings: NewsHeading[]
}

/** 可用于列表、详情和搜索的动态文章文档。 */
export interface NewsDocument extends ParsedNewsMarkdown {
  /** 从 Markdown 文件名生成的文章路由标识。 */
  slug: string
  /** 文章作者署名。 */
  author: string
  /** 文章分类；无分类时可为空。 */
  category: string | null
  /** 文章标签。 */
  tags: string[]
  /** 文章标题。 */
  title: string
  /** 文章日期字符串。 */
  date: string
}

/** 文章在当前排序列表中的相邻文档。 */
export interface AdjacentNewsDocuments {
  /** 当前排序中位于前一项的文章；不存在时为 null。 */
  previous: NewsDocument | null
  /** 当前排序中位于后一项的文章；不存在时为 null。 */
  next: NewsDocument | null
}
