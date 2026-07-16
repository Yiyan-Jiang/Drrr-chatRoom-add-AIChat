/**
 * @parm 组件用途：展示主布局右侧功能入口和提示区。
 */
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { friendsApi } from '@/api/friends'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { AICharacter } from '@/types/ai'
import type { Friend } from '@/types/friends'
import { logger } from '@/utils/logger'
import { getUserDisplayName } from '@/utils/userDisplayName'

type AICharacterItem = {
  id: AICharacter
  label: string
  avatarKey: string
}

const AI_CHARACTERS: AICharacterItem[] = [
  { id: 'sakura', label: '小樱', avatarKey: 'pink' },
  { id: 'rin', label: '凛', avatarKey: 'gray' },
  { id: 'mio', label: '澪', avatarKey: 'zaika' },
  { id: 'yang', label: '葵', avatarKey: 'kanra' },
]

export default function RightSidebar() {
  const pageSize = 8
  const [friendPage, setFriendPage] = useState(1)
  const [friends, setFriends] = useState<Friend[]>([])
  const [hasMoreFriends, setHasMoreFriends] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function loadFriends() {
      try {
        const page = await friendsApi.listFriends({ page: friendPage, pageSize })
        if (cancelled) return
        setFriends(page.items)
        setHasMoreFriends(page.has_more)
      } catch (error) {
        logger.error('[right-sidebar] failed to load friends', {
          message: error instanceof Error ? error.message : String(error),
        })
      }
    }
    loadFriends()
    return () => {
      cancelled = true
    }
  }, [friendPage])

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    logger.debug('搜索接口待实现')
  }

  return (
    <div className="ml-1 flex h-[80%] flex-col border-2 border-white bg-[#0D0D0D]">
      <form
        action=""
        onSubmit={handleSearch}
        className="mb-2 h-7 w-full border-b border-white bg-[#45474A] leading-7"
      >
        <input
          type="text"
          placeholder="搜索"
          className="h-full w-full border-none px-2 outline-none"
        />
      </form>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="grid auto-rows-[90px] grid-cols-3 lg:grid-cols-4">
          {AI_CHARACTERS.map((char) => {
            const assets = resolveChatAvatarAssets(char.avatarKey)

            return (
              <Link
                key={char.id}
                to={`/ai-chat?char=${char.id}`}
                className="flex h-[90px] flex-col items-center justify-start bg-transparent py-2 transition hover:scale-105"
              >
                <img
                  src={assets.avatar}
                  alt={char.label}
                  className="mb-0.5 h-14 w-14 shrink-0 object-cover"
                />
                <span className="max-w-14 truncate text-xs font-medium leading-4 text-gray-300">{char.label}</span>
              </Link>
            )
          })}
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
                <span className="max-w-14 truncate text-xs font-medium leading-4 text-gray-300">{label}</span>
              </Link>
            )
          })}
        </div>
      </div>
      <div className="mt-auto flex items-center justify-center gap-2 border-t border-zinc-800 py-2 text-xs text-zinc-300">
        <button
          type="button"
          disabled={friendPage <= 1}
          onClick={() => setFriendPage((page) => Math.max(1, page - 1))}
          className="border border-zinc-700 px-2 py-1 disabled:text-zinc-600"
        >
          上一页
        </button>
        <span>{friendPage}</span>
        <button
          type="button"
          disabled={!hasMoreFriends}
          onClick={() => setFriendPage((page) => page + 1)}
          className="border border-zinc-700 px-2 py-1 disabled:text-zinc-600"
        >
          下一页
        </button>
      </div>
    </div>
  )
}
