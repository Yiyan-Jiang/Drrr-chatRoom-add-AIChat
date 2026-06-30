import { useNavigate } from 'react-router-dom'
import PostCard from '@/components/posts/PostCard'
import PostEditor from '@/components/posts/PostEditor'
import { usePosts } from '@/hooks/usePosts'

export default function PostsFeed() {
  const navigate = useNavigate()
  const { posts, loadState, errorMessage, isCreating, loadPosts, createPost } = usePosts()

  const handleCreate = async (payload: { title: string; content: string }) => {
    const created = await createPost(payload)
    navigate(`/posts/${created.id}`)
  }

  return (
    <main className="relative flex h-full min-h-0 flex-col overflow-hidden bg-black text-zinc-100">
      <section className="min-h-0 flex-1 overflow-auto bg-[#090909] px-4 py-5 sm:px-6">
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          <header className="border-b border-zinc-800 pb-4">
            <div className="flex items-end justify-between gap-3">
              <h1 className="text-2xl font-semibold text-white">帖子</h1>
              <button
                className="rounded border border-zinc-700 px-3 py-1.5 text-sm text-zinc-200 transition hover:border-zinc-500 hover:bg-zinc-900"
                type="button"
                onClick={loadPosts}
                disabled={loadState === 'loading'}
              >
                {loadState === 'loading' ? '刷新中' : '刷新'}
              </button>
            </div>
          </header>

          {loadState === 'loading' && (
            <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
              正在加载帖子...
            </div>
          )}

          {loadState === 'error' && (
            <div className="rounded border border-red-900/70 bg-red-950/30 px-4 py-5">
              <p className="text-sm text-red-100">{errorMessage}</p>
              <button
                className="mt-4 rounded border border-red-800 px-3 py-1.5 text-sm text-red-100 transition hover:bg-red-950"
                type="button"
                onClick={loadPosts}
              >
                重试
              </button>
            </div>
          )}

          {loadState === 'success' && posts.length === 0 && (
            <div className="rounded border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
              还没有帖子。
            </div>
          )}

          {posts.length > 0 && (
            <div className="flex flex-col gap-3">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </div>
      </section>

      <PostEditor disabled={isCreating} onSubmit={handleCreate} />
    </main>
  )
}
