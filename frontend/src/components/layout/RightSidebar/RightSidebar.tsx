/**
 * 主布局右侧的好友分页与私聊入口。
 */
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { friendsApi } from '@/api/friends'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { Friend } from '@/types/friends'
import { logger } from '@/utils/logger'
import { getUserDisplayName } from '@/utils/userDisplayName'

/** 按昵称或用户名搜索并分页加载好友，提供私聊入口。 */
export default function RightSidebar() {
  const pageSize = 8
  const [searchInput, setSearchInput] = useState('')
  const [friendQuery, setFriendQuery] = useState({ page: 1, search: '' })
  const [friends, setFriends] = useState<Friend[]>([])
  const [hasMoreFriends, setHasMoreFriends] = useState(false)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadFriends() {
      try {
        const page = await friendsApi.listFriends({
          page: friendQuery.page,
          pageSize,
          search: friendQuery.search,
        })
        if (cancelled) return
        setFriends(page.items)
        setHasMoreFriends(page.has_more)
      } catch (error) {
        if (cancelled) return
        setErrorMessage('加载好友失败，请重新搜索。')
        logger.error('[right-sidebar] failed to load friends', {
          message: error instanceof Error ? error.message : String(error),
        })
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadFriends()
    return () => {
      cancelled = true
    }
  }, [friendQuery])

  /** 更新查询并显示加载状态，重复提交相同条件时也重新请求。 */
  const changeQuery = (page: number, search: string) => {
    setLoading(true)
    setErrorMessage('')
    setFriendQuery({ page, search })
  }

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    changeQuery(1, searchInput.trim())
  }

  return (
    <div className="ml-1 flex h-full flex-col border-2 border-white bg-[#0D0D0D]">
      <form
        action=""
        onSubmit={handleSearch}
        className="mb-2 flex h-7 w-full shrink-0 border-b border-white bg-[#45474A] leading-7 text-white"
      >
        <input
          type="text"
          aria-label="搜索好友"
          placeholder="昵称或用户名"
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
          className="h-full min-w-0 flex-1 border-none px-2 outline-none"
        />
        {(searchInput || friendQuery.search) && (
          <button
            type="button"
            aria-label="清空好友搜索"
            title="清空好友搜索"
            onClick={() => {
              setSearchInput('')
              changeQuery(1, '')
            }}
            className="h-full px-2 hover:bg-zinc-600"
          >
            ×
          </button>
        )}
        <button
          type="submit"
          className="h-full shrink-0 border-l border-white px-2 text-xs hover:bg-zinc-600"
        >
          搜索
        </button>
      </form>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <p
            role="status"
            className="px-2 py-4 text-center text-xs text-zinc-400"
          >
            正在加载好友...
          </p>
        ) : errorMessage ? (
          <p
            role="alert"
            className="px-2 py-4 text-center text-xs text-red-300"
          >
            {errorMessage}
          </p>
        ) : friends.length === 0 ? (
          <p
            role="status"
            className="px-2 py-4 text-center text-xs text-zinc-400"
          >
            {friendQuery.search ? '没有匹配的好友' : '暂无好友'}
          </p>
        ) : (
          <div className="grid auto-rows-[90px] grid-cols-3 lg:grid-cols-4">
            {friends.map((friend) => {
              const assets = resolveChatAvatarAssets(friend.user.avatar_key)
              const label = getUserDisplayName(friend.user)

              return (
                <Link
                  key={friend.user.id}
                  to={`/private-chat/${friend.user.id}`}
                  className="flex h-[90px] flex-col items-center justify-start bg-transparent py-2 transition hover:scale-105"
                >
                  <img
                    src={assets.avatar}
                    alt={label}
                    className="mb-0.5 h-14 w-14 shrink-0 object-cover"
                  />
                  <span className="max-w-14 truncate text-xs font-medium leading-4 text-gray-300">
                    {label}
                  </span>
                </Link>
              )
            })}
          </div>
        )}
      </div>
      <div className="mt-auto flex items-center justify-center gap-2 border-t border-zinc-800 py-2 text-xs text-zinc-300">
        <button
          type="button"
          disabled={loading || Boolean(errorMessage) || friendQuery.page <= 1}
          onClick={() => changeQuery(friendQuery.page - 1, friendQuery.search)}
          className="border border-zinc-700 px-2 py-1 disabled:text-zinc-600"
        >
          上一页
        </button>
        <span>{friendQuery.page}</span>
        <button
          type="button"
          disabled={loading || Boolean(errorMessage) || !hasMoreFriends}
          onClick={() => changeQuery(friendQuery.page + 1, friendQuery.search)}
          className="border border-zinc-700 px-2 py-1 disabled:text-zinc-600"
        >
          下一页
        </button>
      </div>
    </div>
  )
}
