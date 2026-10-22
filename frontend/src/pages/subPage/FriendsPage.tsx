/** 展示好友发布的帖子，并提供游标分页与空状态入口。 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { friendsApi } from '@/api/friends'
import { postsApi, type PostListItem } from '@/api/posts'
import PostCard from '@/components/posts/PostCard'
import { logger } from '@/utils/logger'

const pageSize = 20

/** 展示好友发布的帖子，并提供游标分页与空状态入口。 */
export default function FriendsPage() {
  const [posts, setPosts] = useState<PostListItem[]>([])
  const [friendCount, setFriendCount] = useState<number | null>(null)
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState(false)
  const requestId = useRef(0)

  /** 刷新好友动态首页并同步好友总数。 */
  const loadFeed = useCallback(async () => {
    const currentRequest = ++requestId.current
    setLoading(true)
    setLoadingMore(false)
    setError(false)
    try {
      const [page, friends] = await Promise.all([
        postsApi.list({ limit: pageSize, friends_only: true }),
        friendsApi.listFriends({ page: 1, pageSize: 1 }),
      ])
      if (requestId.current !== currentRequest) return
      setPosts(page.items)
      setNextCursor(page.next_cursor)
      setHasMore(page.has_more)
      setFriendCount(friends.total)
    } catch (loadError) {
      if (requestId.current !== currentRequest) return
      logger.error('[friends-feed] failed to load friends feed', {
        message:
          loadError instanceof Error ? loadError.message : String(loadError),
      })
      setError(true)
    } finally {
      if (requestId.current === currentRequest) setLoading(false)
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadFeed()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [loadFeed])

  /** 使用下一条游标追加好友帖子。 */
  const loadMore = async () => {
    if (nextCursor === null || loadingMore) return
    const currentRequest = requestId.current
    setLoadingMore(true)
    try {
      const page = await postsApi.list({
        limit: pageSize,
        cursor: nextCursor,
        friends_only: true,
      })
      if (requestId.current !== currentRequest) return
      setPosts((currentPosts) => [...currentPosts, ...page.items])
      setNextCursor(page.next_cursor)
      setHasMore(page.has_more)
    } catch (loadError) {
      if (requestId.current !== currentRequest) return
      logger.error('[friends-feed] failed to load more posts', {
        message:
          loadError instanceof Error ? loadError.message : String(loadError),
      })
      setError(true)
    } finally {
      if (requestId.current === currentRequest) setLoadingMore(false)
    }
  }

  return (
    <main className="h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-6 sm:px-6">
        <header className="flex items-end justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <h1 className="text-2xl font-semibold text-white">好友动态</h1>
            <p className="mt-2 text-sm text-zinc-500">好友最近发布的帖子</p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/friends/manage"
              className="border border-zinc-700 px-3 py-1.5 text-sm text-zinc-200 transition hover:border-zinc-500"
            >
              管理好友
            </Link>
            <button
              type="button"
              onClick={() => void loadFeed()}
              disabled={loading}
              className="border border-zinc-700 px-3 py-1.5 text-sm text-zinc-200 transition hover:border-zinc-500 disabled:cursor-not-allowed disabled:text-zinc-600"
            >
              {loading ? '刷新中...' : '刷新'}
            </button>
          </div>
        </header>

        {loading && posts.length === 0 && (
          <p className="border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            正在加载好友动态...
          </p>
        )}

        {error && (
          <div
            role="alert"
            className="flex flex-wrap items-center justify-between gap-3 border border-red-900/70 bg-red-950/30 px-4 py-4"
          >
            <p className="text-sm text-red-100">好友动态加载失败，请重试。</p>
            <button
              type="button"
              onClick={() => void loadFeed()}
              disabled={loading}
              className="border border-red-800 px-3 py-1.5 text-sm text-red-100 transition hover:bg-red-950 disabled:cursor-not-allowed disabled:text-zinc-600"
            >
              重新加载
            </button>
          </div>
        )}

        {!loading && !error && friendCount === 0 && (
          <div className="border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
            <p>还没有添加好友，去添加好友吧。</p>
            <Link
              to="/friends/manage"
              className="mt-3 inline-block text-zinc-200 underline underline-offset-4 hover:text-white"
            >
              添加好友
            </Link>
          </div>
        )}

        {!loading &&
          !error &&
          friendCount !== null &&
          friendCount > 0 &&
          posts.length === 0 && (
            <p className="border border-zinc-800 bg-zinc-950 px-4 py-8 text-center text-sm text-zinc-400">
              这里还是空空如也~
            </p>
          )}

        {posts.length > 0 && (
          <div className="flex flex-col gap-3">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        )}

        {hasMore && !error && (
          <button
            type="button"
            onClick={() => void loadMore()}
            disabled={loadingMore || loading}
            className="self-center border border-zinc-700 px-4 py-2 text-sm text-zinc-200 transition hover:border-zinc-500 disabled:cursor-not-allowed disabled:text-zinc-600"
          >
            {loadingMore ? '加载中...' : '加载更多'}
          </button>
        )}
      </div>
    </main>
  )
}
