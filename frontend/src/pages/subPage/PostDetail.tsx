import { Link, useParams } from 'react-router-dom'
import CommentComposer from '@/components/posts/CommentComposer'
import CommentList from '@/components/posts/CommentList'
import PostAuthorAvatar, { getPostAuthorName } from '@/components/posts/PostAuthorAvatar'
import { CommentIcon, FavoriteIcon, LikeIcon } from '@/components/posts/PostStatsIcons'
import PostMarkdownArticle from '@/features/posts/PostMarkdownArticle'
import { usePostDetail } from '@/hooks/usePostDetail'
import logoSource from '@/assets/icon/Logo/logo.png'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export default function PostDetail() {
  const { postId } = useParams()
  const parsedPostId = Number(postId)
  const {
    post,
    comments,
    loadState,
    errorMessage,
    isMutating,
    commentDraft,
    setCommentDraft,
    loadPost,
    toggleLike,
    toggleFavorite,
    submitComment,
  } = usePostDetail(Number.isInteger(parsedPostId) && parsedPostId > 0 ? parsedPostId : null)

  if (loadState === 'loading') {
    return (
      <main className="min-h-screen bg-[#f6f6f7] pt-14 text-[#213547]">
        <PostHeader />
        <section className="mx-auto max-w-4xl px-4 py-5 sm:px-6">
          <div className="rounded-lg border border-[#e2e2e3] bg-white px-4 py-8 text-center text-sm text-[#67676c]">
            正在加载帖子...
          </div>
        </section>
      </main>
    )
  }

  if (loadState === 'error' || !post) {
    return (
      <main className="min-h-screen bg-[#f6f6f7] pt-14 text-[#213547]">
        <PostHeader />
        <section className="mx-auto max-w-4xl px-4 py-5 sm:px-6">
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-5">
          <p className="text-sm text-red-700">{errorMessage || '帖子不存在或已被删除。'}</p>
          <div className="mt-4 flex gap-3">
            <button
              className="rounded border border-red-200 px-3 py-1.5 text-sm text-red-700 transition hover:bg-red-100"
              type="button"
              onClick={loadPost}
            >
              重试
            </button>
            <Link className="rounded border border-[#e2e2e3] bg-white px-3 py-1.5 text-sm text-[#3451b2]" to="/home/posts">
              返回帖子
            </Link>
          </div>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#f6f6f7] pt-14 text-[#213547]">
      <PostHeader />
      <section className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-5 sm:px-6">
        <Link className="w-fit text-sm font-medium text-[#3451b2] transition hover:text-[#213547]" to="/home/posts">
          返回帖子
        </Link>

        <article className="rounded-xl border border-[#e2e2e3] bg-white px-5 py-6 shadow-sm sm:px-8">
          <header className="border-b border-[#e2e2e3] pb-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
              <PostAuthorAvatar author={post.author} className="h-12 w-12" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2 text-xs text-[#67676c]">
                  <span>by {getPostAuthorName(post.author)}</span>
                  <span>更新于 {formatDate(post.updated_at)}</span>
                </div>
                <h1 className="mt-4 text-3xl font-bold tracking-tight text-[#213547]">{post.title}</h1>
              </div>
            </div>
          </header>

          <div className="mt-6">
            <PostMarkdownArticle markdown={post.content} />
          </div>

          <footer className="mt-8 flex justify-end border-t border-[#e2e2e3] pt-4">
            <div className="flex flex-wrap justify-end gap-2 text-sm">
              <button
                aria-label={`点赞，当前 ${post.likes_count} 个赞`}
                className={`inline-flex h-9 items-center gap-1.5 rounded border px-3 transition ${
                  post.liked_by_me
                    ? 'border-[#3451b2] bg-[#f1f3ff] text-[#3451b2]'
                    : 'border-[#e2e2e3] text-[#3c3c43] hover:border-[#3451b2] hover:text-[#3451b2]'
                }`}
                type="button"
                disabled={isMutating}
                onClick={() => void toggleLike()}
              >
                <LikeIcon className={post.liked_by_me ? 'fill-current' : undefined} />
                <span>{post.likes_count}</span>
                <span>赞</span>
              </button>
              <button
                aria-label={`收藏，当前 ${post.favorites_count} 个收藏`}
                className={`inline-flex h-9 items-center gap-1.5 rounded border px-3 transition ${
                  post.favorited_by_me
                    ? 'border-amber-400 bg-amber-50 text-amber-700'
                    : 'border-[#e2e2e3] text-[#3c3c43] hover:border-amber-400 hover:text-amber-700'
                }`}
                type="button"
                disabled={isMutating}
                onClick={() => void toggleFavorite()}
              >
                <FavoriteIcon className={post.favorited_by_me ? 'fill-current' : undefined} />
                <span>{post.favorites_count}</span>
                <span>收藏</span>
              </button>
              <span
                aria-label={`评论，当前 ${post.comments_count} 条评论`}
                className="inline-flex h-9 items-center gap-1.5 rounded border border-[#e2e2e3] px-3 text-[#67676c]"
              >
                <CommentIcon />
                <span>{post.comments_count}</span>
                <span>评论</span>
              </span>
            </div>
          </footer>
        </article>

        {errorMessage && loadState === 'success' && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
          </div>
        )}

        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold text-[#213547]">评论</h2>
          <CommentComposer
            value={commentDraft}
            onChange={setCommentDraft}
            onSubmit={submitComment}
            disabled={isMutating}
          />
          <CommentList comments={comments} />
        </section>
      </section>
    </main>
  )
}

function PostHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-zinc-900 bg-black/95">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link className="flex min-w-0 items-center gap-3" to="/home/posts">
          <img
            alt="Drrr logo"
            className="h-8 w-8 shrink-0 object-contain"
            src={logoSource}
          />
          <span className="truncate text-sm font-semibold text-zinc-100">
            Posts
          </span>
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link className="text-zinc-400 transition hover:text-zinc-100" to="/home/posts">
            帖子
          </Link>
          <Link className="text-zinc-400 transition hover:text-zinc-100" to="/home/rooms">
            聊天室
          </Link>
        </nav>
      </div>
    </header>
  )
}
