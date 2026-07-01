import type { PostComment } from '@/api'
import PostAuthorAvatar from '@/components/posts/PostAuthorAvatar'
import { getPostAuthorName } from '@/components/posts/postAuthorName'
import { MarkdownRenderer } from '@/features/news/markdownRenderer'

type CommentListProps = {
  comments: PostComment[]
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export default function CommentList({ comments }: CommentListProps) {
  if (comments.length === 0) {
    return (
      <div className="rounded-lg border border-[#e2e2e3] bg-white px-4 py-6 text-center text-sm text-[#67676c] shadow-sm">
        暂无评论。
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {comments.map((comment) => (
        <article className="rounded-lg border border-[#e2e2e3] bg-white p-4 shadow-sm" key={comment.id}>
          <div className="flex gap-3">
            <PostAuthorAvatar author={comment.author} className="h-9 w-9" />
            <div className="min-w-0 flex-1">
              <p className="text-xs text-[#67676c]">
                {getPostAuthorName(comment.author)} · {formatDate(comment.updated_at)}
              </p>
              <div className="mt-3">
                <MarkdownRenderer markdown={comment.content} />
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}
