/** 展示帖子摘要、作者和互动计数，并提供详情链接。 */
import { Link } from 'react-router-dom'
import type { PostListItem } from '@/api'
import PostAuthorAvatar from '@/components/posts/PostAuthorAvatar'
import { getPostAuthorName } from '@/components/posts/postAuthorName'
import {
  CommentIcon,
  FavoriteIcon,
  LikeIcon,
} from '@/components/posts/PostStatsIcons'
import { MarkdownRenderer } from '@/features/news/markdownRenderer'

/** 帖子列表卡片数据。 */
type PostCardProps = {
  /** 包含预览正文和互动计数的帖子摘要。 */
  post: PostListItem
}

/** 按本地时区展示帖子更新的月日和时分。 */
function formatDate(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

/** 展示帖子摘要、作者和互动计数，并提供详情链接。 */
export default function PostCard({ post }: PostCardProps) {
  const authorName = getPostAuthorName(post.author)

  return (
    <article className="rounded border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900/80">
      <Link className="block" to={`/posts/${post.id}`}>
        <div className="flex gap-3">
          <PostAuthorAvatar author={post.author} />
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-semibold text-white">
                  {post.title}
                </h2>
                <p className="mt-1 text-xs text-zinc-500">
                  {authorName} · 更新于 {formatDate(post.updated_at)}
                </p>
              </div>
            </div>

            {post.content_preview && (
              <div className="mt-3 line-clamp-3 text-sm leading-6 text-zinc-300">
                <MarkdownRenderer
                  markdown={post.content_preview}
                  components={{
                    p: ({ children }) => (
                      <p className="text-sm leading-6 text-zinc-300">
                        {children}
                      </p>
                    ),
                    h1: ({ children }) => (
                      <p className="text-sm font-semibold leading-6 text-zinc-100">
                        {children}
                      </p>
                    ),
                    h2: ({ children }) => (
                      <p className="text-sm font-semibold leading-6 text-zinc-100">
                        {children}
                      </p>
                    ),
                    h3: ({ children }) => (
                      <p className="text-sm font-semibold leading-6 text-zinc-100">
                        {children}
                      </p>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc pl-5 text-sm leading-6 text-zinc-300">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal pl-5 text-sm leading-6 text-zinc-300">
                        {children}
                      </ol>
                    ),
                    img: ({ alt }) => (
                      <span className="text-zinc-500">{alt || '[图片]'}</span>
                    ),
                  }}
                />
              </div>
            )}

            <div className="mt-3 flex justify-end">
              <div className="flex items-center gap-3 text-xs text-zinc-500">
                <span
                  aria-label={`${post.likes_count} 个赞`}
                  className="inline-flex items-center gap-1"
                >
                  <LikeIcon />
                  <span>{post.likes_count}</span>
                </span>
                <span
                  aria-label={`${post.favorites_count} 个收藏`}
                  className="inline-flex items-center gap-1"
                >
                  <FavoriteIcon />
                  <span>{post.favorites_count}</span>
                </span>
                <span
                  aria-label={`${post.comments_count} 条评论`}
                  className="inline-flex items-center gap-1"
                >
                  <CommentIcon />
                  <span>{post.comments_count}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </Link>
    </article>
  )
}
