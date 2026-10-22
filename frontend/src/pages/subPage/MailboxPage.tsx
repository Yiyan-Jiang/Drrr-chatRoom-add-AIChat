/** 展示最近私聊、未读数量和会话分页。 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { privateMessagesApi } from '@/api/privateMessages'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { socketManager } from '@/services/socket'
import type { PrivateConversation } from '@/types/privateMessages'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { logger } from '@/utils/logger'

const pageSize = 20

/** 将消息时间转换为邮箱列表中的本地日期时间。 */
function formatMessageTime(value: string) {
  const date = new Date(value)
  return date.toLocaleString(undefined, {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** 展示最近私聊、未读数量和会话分页。 */
export default function MailboxPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<PrivateConversation[]>([])
  const [page, setPage] = useState(1)
  const [retryVersion, setRetryVersion] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const requestId = useRef(0)

  const loadConversations = useCallback(
    async (isActive: () => boolean = () => true) => {
      const currentRequest = ++requestId.current
      try {
        const response = await privateMessagesApi.getConversations({
          page,
          pageSize,
        })
        if (requestId.current !== currentRequest || !isActive()) return
        setItems(response.items)
        setHasMore(response.has_more)
        setError(null)
      } catch (requestError) {
        if (requestId.current !== currentRequest || !isActive()) return
        logger.error('[mailbox] failed to load conversations', {
          message:
            requestError instanceof Error
              ? requestError.message
              : String(requestError),
        })
        setError('加载邮箱失败，请重试。')
      } finally {
        if (requestId.current === currentRequest && isActive())
          setLoading(false)
      }
    },
    [page],
  )

  useEffect(() => {
    let active = true
    const timer = window.setTimeout(() => {
      void loadConversations(() => active)
    }, 0)
    return () => {
      active = false
      window.clearTimeout(timer)
    }
  }, [loadConversations, retryVersion])

  useEffect(() => {
    const socket = socketManager.getSocket()
    if (!socket) return
    let active = true
    const refresh = () => void loadConversations(() => active)
    socket.on('mailbox_changed', refresh)
    socket.on('connect', refresh)
    return () => {
      active = false
      socket.off('mailbox_changed', refresh)
      socket.off('connect', refresh)
    }
  }, [loadConversations])

  return (
    <div className="h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-5 px-4 py-6 sm:px-8">
        <header className="flex flex-wrap items-end justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <h1 className="text-2xl font-semibold text-white">邮箱</h1>
            <p className="mt-2 text-sm text-zinc-500">最近的私聊会话</p>
          </div>
          <Link
            to="/friends"
            className="border border-zinc-700 px-3 py-2 text-sm transition hover:border-cyan-500"
          >
            好友列表
          </Link>
        </header>

        <section className="border border-zinc-800 bg-zinc-950/40">
          <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
            <h2 className="text-sm font-semibold text-white">会话</h2>
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <button
                type="button"
                disabled={page <= 1 || loading}
                onClick={() => {
                  setLoading(true)
                  setError(null)
                  setPage((current) => Math.max(1, current - 1))
                }}
                className="border border-zinc-700 px-2 py-1 transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
              >
                上一页
              </button>
              <span>{page}</span>
              <button
                type="button"
                disabled={!hasMore || loading}
                onClick={() => {
                  setLoading(true)
                  setError(null)
                  setPage((current) => current + 1)
                }}
                className="border border-zinc-700 px-2 py-1 transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
              >
                下一页
              </button>
            </div>
          </div>

          {loading && items.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">
              正在加载会话...
            </p>
          ) : error ? (
            <div className="flex flex-col items-center gap-3 px-4 py-8 text-center">
              <p role="alert" className="text-sm text-red-300">
                {error}
              </p>
              <button
                type="button"
                onClick={() => {
                  setLoading(true)
                  setError(null)
                  setRetryVersion((version) => version + 1)
                }}
                className="border border-zinc-700 px-3 py-1.5 text-sm transition hover:border-cyan-500"
              >
                重试
              </button>
            </div>
          ) : items.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">
              暂无私聊会话。可以先前往好友列表开始聊天。
            </p>
          ) : (
            <ul className="divide-y divide-zinc-800">
              {items.map((conversation) => {
                const {
                  user,
                  latest_message: latestMessage,
                  unread_count: unreadCount,
                } = conversation
                const assets = resolveChatAvatarAssets(user.avatar_key)
                const isOwn = latestMessage.sender_id !== user.id
                return (
                  <li key={user.id}>
                    <button
                      type="button"
                      onClick={() => navigate(`/private-chat/${user.id}`)}
                      className="flex w-full items-center gap-3 px-4 py-4 text-left transition hover:bg-zinc-900/70 focus-visible:outline focus-visible:outline-1 focus-visible:outline-cyan-500"
                    >
                      <img
                        src={assets.avatar}
                        alt=""
                        className="h-12 w-12 shrink-0 object-cover"
                        loading="lazy"
                      />
                      <span className="min-w-0 flex-1">
                        <span className="flex items-center justify-between gap-3">
                          <span className="truncate text-sm font-semibold text-zinc-100">
                            {getUserDisplayName(user)}
                          </span>
                          <span className="shrink-0 text-xs text-zinc-500">
                            {formatMessageTime(latestMessage.created_at)}
                          </span>
                        </span>
                        <span className="mt-1 flex items-center justify-between gap-3">
                          <span className="truncate text-sm text-zinc-400">
                            {isOwn ? '我: ' : ''}
                            {latestMessage.content}
                          </span>
                          {unreadCount > 0 ? (
                            <span
                              aria-label={`${unreadCount} 条未读消息`}
                              className="shrink-0 rounded-full bg-cyan-500 px-2 py-0.5 text-xs font-semibold text-black"
                            >
                              {unreadCount > 99 ? '99+' : unreadCount}
                            </span>
                          ) : null}
                        </span>
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
