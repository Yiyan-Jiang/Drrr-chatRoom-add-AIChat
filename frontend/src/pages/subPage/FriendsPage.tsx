import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { friendsApi } from '@/api/friends'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { Friend, FriendRequest } from '@/types/chat'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { logger } from '@/utils/logger'

const pageSize = 12

function requestName(request: FriendRequest, side: 'requester' | 'recipient') {
  return getUserDisplayName(side === 'requester' ? request.requester : request.recipient)
}

function filterPendingFriendRequests(requests: FriendRequest[]) {
  return requests.filter((request) => request.status === 'pending')
}

export default function FriendsPage() {
  const navigate = useNavigate()
  const [friends, setFriends] = useState<Friend[]>([])
  const [incomingFriendRequests, setIncomingFriendRequests] = useState<FriendRequest[]>([])
  const [outgoingFriendRequests, setOutgoingFriendRequests] = useState<FriendRequest[]>([])
  const [friendPage, setFriendPage] = useState(1)
  const [hasMoreFriends, setHasMoreFriends] = useState(false)
  const [loading, setLoading] = useState(true)
  const [busyRequestId, setBusyRequestId] = useState<number | null>(null)
  const [busyFriendId, setBusyFriendId] = useState<number | null>(null)

  const loadFriends = useCallback(async () => {
    const page = await friendsApi.listFriends({ page: friendPage, pageSize })
    setFriends(page.items)
    setHasMoreFriends(page.has_more)
  }, [friendPage])

  const loadRequests = useCallback(async () => {
    const [incoming, outgoing] = await Promise.all([
      friendsApi.listRequests('incoming'),
      friendsApi.listRequests('outgoing'),
    ])
    setIncomingFriendRequests(filterPendingFriendRequests(incoming.items))
    setOutgoingFriendRequests(filterPendingFriendRequests(outgoing.items))
  }, [])

  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      await Promise.all([loadFriends(), loadRequests()])
    } catch (error) {
      logger.error('[friends-page] failed to load friends', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('加载好友信息失败')
    } finally {
      setLoading(false)
    }
  }, [loadFriends, loadRequests])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadAll()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [loadAll])

  const acceptRequest = async (requestId: number) => {
    setBusyRequestId(requestId)
    try {
      await friendsApi.acceptRequest(requestId)
      await Promise.all([loadFriends(), loadRequests()])
      toast.success('已接受好友申请')
    } finally {
      setBusyRequestId(null)
    }
  }

  const rejectRequest = async (requestId: number) => {
    setBusyRequestId(requestId)
    try {
      await friendsApi.rejectRequest(requestId)
      await loadRequests()
      toast.success('已拒绝好友申请')
    } finally {
      setBusyRequestId(null)
    }
  }

  const cancelRequest = async (requestId: number) => {
    setBusyRequestId(requestId)
    try {
      await friendsApi.cancelRequest(requestId)
      await loadRequests()
      toast.success('已取消好友申请')
    } finally {
      setBusyRequestId(null)
    }
  }

  const deleteFriend = async (friendId: number) => {
    setBusyFriendId(friendId)
    try {
      await friendsApi.deleteFriend(friendId)
      await loadFriends()
      toast.success('已删除好友')
    } finally {
      setBusyFriendId(null)
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-8">
        <header className="border-b border-zinc-800 pb-4">
          <h1 className="text-2xl font-semibold tracking-normal text-white">友达</h1>
          <p className="mt-2 text-sm text-zinc-500">管理好友、处理申请，并从这里发起私聊。</p>
        </header>

        <section className="rounded-sm border border-zinc-800 bg-zinc-950/40">
          <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
            <h2 className="text-sm font-semibold text-white">好友列表</h2>
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <button
                type="button"
                disabled={friendPage <= 1 || loading}
                onClick={() => setFriendPage((page) => Math.max(1, page - 1))}
                className="border border-zinc-700 px-2 py-1 transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
              >
                上一页
              </button>
              <span>{friendPage}</span>
              <button
                type="button"
                disabled={!hasMoreFriends || loading}
                onClick={() => setFriendPage((page) => page + 1)}
                className="border border-zinc-700 px-2 py-1 transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
              >
                下一页
              </button>
            </div>
          </div>

          {loading ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">加载中...</p>
          ) : friends.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">暂无好友。可以在聊天室或帖子头像上发起好友申请。</p>
          ) : (
            <ul className="grid gap-3 p-4 md:grid-cols-2">
              {friends.map((friend) => {
                const assets = resolveChatAvatarAssets(friend.user.avatar_key)
                const label = getUserDisplayName(friend.user)
                return (
                  <li key={friend.user.id} className="flex items-center gap-3 border border-zinc-800 bg-black px-3 py-3">
                    <img src={assets.avatar} alt="" className="h-12 w-12 shrink-0 object-cover" loading="lazy" />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-semibold text-zinc-100">{label}</div>
                      <div className="truncate text-xs text-zinc-500">@{friend.user.username}</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => navigate(`/private-chat/${friend.user.id}`)}
                      className="border border-zinc-700 px-3 py-1.5 text-xs transition hover:border-cyan-500"
                    >
                      私聊
                    </button>
                    <button
                      type="button"
                      disabled={busyFriendId === friend.user.id}
                      onClick={() => void deleteFriend(friend.user.id)}
                      className="border border-zinc-800 px-3 py-1.5 text-xs text-zinc-400 transition hover:border-red-500 hover:text-red-300 disabled:cursor-not-allowed"
                    >
                      删除
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-sm border border-zinc-800 bg-zinc-950/40">
            <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold text-white">收到的申请</h2>
            {incomingFriendRequests.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-500">暂无收到的好友申请。</p>
            ) : (
              <ul className="divide-y divide-zinc-800">
                {incomingFriendRequests.map((request) => (
                  <li key={request.id} className="flex items-center justify-between gap-3 px-4 py-3">
                    <span className="min-w-0 truncate text-sm text-zinc-200">{requestName(request, 'requester')}</span>
                    <div className="flex shrink-0 gap-2">
                      <button
                        type="button"
                        disabled={busyRequestId === request.id}
                        onClick={() => void acceptRequest(request.id)}
                        className="border border-zinc-700 px-2 py-1 text-xs transition hover:border-cyan-500 disabled:cursor-not-allowed"
                      >
                        接受
                      </button>
                      <button
                        type="button"
                        disabled={busyRequestId === request.id}
                        onClick={() => void rejectRequest(request.id)}
                        className="border border-zinc-700 px-2 py-1 text-xs transition hover:border-red-500 disabled:cursor-not-allowed"
                      >
                        拒绝
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-sm border border-zinc-800 bg-zinc-950/40">
            <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold text-white">发出的申请</h2>
            {outgoingFriendRequests.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-500">暂无发出的好友申请。</p>
            ) : (
              <ul className="divide-y divide-zinc-800">
                {outgoingFriendRequests.map((request) => (
                  <li key={request.id} className="flex items-center justify-between gap-3 px-4 py-3">
                    <span className="min-w-0 truncate text-sm text-zinc-200">{requestName(request, 'recipient')}</span>
                    <button
                      type="button"
                      disabled={busyRequestId === request.id}
                      onClick={() => void cancelRequest(request.id)}
                      className="shrink-0 border border-zinc-700 px-2 py-1 text-xs transition hover:border-red-500 disabled:cursor-not-allowed"
                    >
                      取消
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
