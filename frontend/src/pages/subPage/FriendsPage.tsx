/** 展示好友列表和待处理申请，提供好友申请处理与删除入口。 */
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { friendsApi } from '@/api/friends'
import { usersApi } from '@/api/users'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { Friend, FriendRequest } from '@/types/friends'
import type { User } from '@/types/user'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { logger } from '@/utils/logger'

const pageSize = 12

/** 返回好友申请中指定一方的显示名。 */
function requestName(request: FriendRequest, side: 'requester' | 'recipient') {
  return getUserDisplayName(
    side === 'requester' ? request.requester : request.recipient,
  )
}

/** 仅保留仍待处理的好友申请。 */
function filterPendingFriendRequests(requests: FriendRequest[]) {
  return requests.filter((request) => request.status === 'pending')
}

/** 展示好友列表和待处理申请，提供好友申请处理与删除入口。 */
export default function FriendsPage() {
  const navigate = useNavigate()
  const [friends, setFriends] = useState<Friend[]>([])
  const [incomingFriendRequests, setIncomingFriendRequests] = useState<
    FriendRequest[]
  >([])
  const [outgoingFriendRequests, setOutgoingFriendRequests] = useState<
    FriendRequest[]
  >([])
  const [friendPage, setFriendPage] = useState(1)
  const [friendSearchInput, setFriendSearchInput] = useState('')
  const [friendSearch, setFriendSearch] = useState('')
  const [hasMoreFriends, setHasMoreFriends] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [username, setUsername] = useState('')
  const [matchedUser, setMatchedUser] = useState<User | null>(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [requestLoading, setRequestLoading] = useState(false)
  const [busyRequestId, setBusyRequestId] = useState<number | null>(null)
  const [busyFriendId, setBusyFriendId] = useState<number | null>(null)
  const friendQueryRef = useRef({
    page: friendPage,
    search: friendSearch,
    version: 0,
  })
  const friendListRequestRef = useRef(0)

  useLayoutEffect(() => {
    if (
      friendQueryRef.current.page !== friendPage ||
      friendQueryRef.current.search !== friendSearch
    ) {
      friendQueryRef.current = {
        page: friendPage,
        search: friendSearch,
        version: friendQueryRef.current.version + 1,
      }
    }
  }, [friendPage, friendSearch])

  const loadFriends = useCallback(async () => {
    const query = friendQueryRef.current
    const requestId = friendListRequestRef.current + 1
    friendListRequestRef.current = requestId
    const page = await friendsApi.listFriends({
      page: query.page,
      pageSize,
      search: query.search || undefined,
    })
    if (
      query.version !== friendQueryRef.current.version ||
      requestId !== friendListRequestRef.current
    ) {
      return
    }
    setFriends(page.items)
    setHasMoreFriends(page.has_more)
  }, [])

  const loadRequests = useCallback(async () => {
    const [incoming, outgoing] = await Promise.all([
      friendsApi.listRequests('incoming'),
      friendsApi.listRequests('outgoing'),
    ])
    setIncomingFriendRequests(filterPendingFriendRequests(incoming.items))
    setOutgoingFriendRequests(filterPendingFriendRequests(outgoing.items))
  }, [])

  const loadAll = useCallback(async () => {
    const queryVersion = friendQueryRef.current.version
    setLoading(true)
    setLoadError(false)
    try {
      await Promise.all([loadFriends(), loadRequests()])
    } catch (error) {
      if (queryVersion !== friendQueryRef.current.version) return
      logger.error('[friends-page] failed to load friends', {
        message: error instanceof Error ? error.message : String(error),
      })
      setLoadError(true)
      toast.error('加载好友信息失败')
    } finally {
      if (queryVersion === friendQueryRef.current.version) {
        setLoading(false)
      }
    }
  }, [loadFriends, loadRequests])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadAll()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [friendPage, friendSearch, loadAll])

  const acceptRequest = async (requestId: number) => {
    setBusyRequestId(requestId)
    try {
      await friendsApi.acceptRequest(requestId)
      await Promise.all([loadFriends(), loadRequests()])
      toast.success('已接受好友申请')
    } catch (error) {
      logger.error('[friends-page] failed to accept friend request', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('接受好友申请失败')
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
    } catch (error) {
      logger.error('[friends-page] failed to reject friend request', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('拒绝好友申请失败')
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
    } catch (error) {
      logger.error('[friends-page] failed to cancel friend request', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('取消好友申请失败')
    } finally {
      setBusyRequestId(null)
    }
  }

  const deleteFriend = async (friendId: number) => {
    if (!window.confirm('确定删除这位好友吗？')) return

    const queryVersion = friendQueryRef.current.version
    setBusyFriendId(friendId)
    try {
      await friendsApi.deleteFriend(friendId)
      toast.success('已删除好友')
      if (
        queryVersion === friendQueryRef.current.version &&
        friends.length === 1 &&
        friendPage > 1
      ) {
        setFriendPage((page) => page - 1)
      } else {
        await loadFriends()
      }
    } catch (error) {
      logger.error('[friends-page] failed to delete friend', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('删除好友失败')
    } finally {
      setBusyFriendId(null)
    }
  }

  /** 提交好友关键词并将分页重置到第一页。 */
  const searchFriends = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFriendPage(1)
    setFriendSearch(friendSearchInput.trim())
  }

  /** 按完整用户名查询用户，并区分用户不存在与请求故障。 */
  const findUser = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const exactUsername = username.trim()
    if (!exactUsername) {
      setMatchedUser(null)
      toast.error('请输入用户名')
      return
    }

    setLookupLoading(true)
    setMatchedUser(null)
    try {
      setMatchedUser(await usersApi.getByUsername(exactUsername))
    } catch (error) {
      logger.error('[friends-page] failed to find user by username', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error(
        axios.isAxiosError(error) && error.response?.status === 404
          ? '未找到该用户名对应的用户'
          : '查找用户失败，请检查网络后重试',
      )
    } finally {
      setLookupLoading(false)
    }
  }

  /** 向已查找到的用户发送好友申请。 */
  const sendFriendRequest = async () => {
    if (!matchedUser) return

    setRequestLoading(true)
    try {
      await friendsApi.createRequest({ recipient_id: matchedUser.id })
      setMatchedUser(null)
      setUsername('')
      await loadRequests()
      toast.success('好友申请已发送')
    } catch (error) {
      logger.error('[friends-page] failed to send friend request', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('发送好友申请失败')
    } finally {
      setRequestLoading(false)
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-8">
        <header className="border-b border-zinc-800 pb-4">
          <h1 className="text-2xl font-semibold tracking-normal text-white">
            友达
          </h1>
          <p className="mt-2 text-sm text-zinc-500">
            管理好友、处理申请，并从这里发起私聊。
          </p>
        </header>

        {loadError && (
          <div
            role="alert"
            className="flex flex-wrap items-center justify-between gap-3 border border-red-900/70 bg-red-950/30 px-4 py-3 text-sm text-red-200"
          >
            <span>好友信息加载失败，列表可能不完整。请重试。</span>
            <button
              type="button"
              disabled={loading}
              onClick={() => void loadAll()}
              className="border border-red-800 px-3 py-1.5 transition hover:border-red-500 disabled:cursor-not-allowed disabled:text-zinc-600"
            >
              {loading ? '加载中...' : '重新加载'}
            </button>
          </div>
        )}

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

          <form
            onSubmit={searchFriends}
            className="flex flex-wrap gap-2 border-b border-zinc-800 px-4 py-3"
          >
            <label htmlFor="friend-search" className="sr-only">
              搜索好友用户名或昵称
            </label>
            <input
              id="friend-search"
              type="search"
              value={friendSearchInput}
              onChange={(event) => setFriendSearchInput(event.target.value)}
              placeholder="搜索用户名或昵称"
              className="min-w-0 flex-1 border border-zinc-700 bg-black px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="border border-zinc-700 px-3 py-2 text-sm transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
            >
              搜索
            </button>
            {friendSearch && (
              <button
                type="button"
                disabled={loading}
                onClick={() => {
                  setFriendSearchInput('')
                  setFriendSearch('')
                  setFriendPage(1)
                }}
                className="border border-zinc-800 px-3 py-2 text-sm text-zinc-400 transition hover:border-zinc-600 disabled:cursor-not-allowed"
              >
                清除搜索
              </button>
            )}
          </form>

          {loading ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">
              加载中...
            </p>
          ) : loadError ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">
              好友列表暂不可用。
            </p>
          ) : friends.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-zinc-500">
              {friendSearch
                ? '没有匹配的好友。'
                : '暂无好友。可以在聊天室或帖子头像上发起好友申请。'}
            </p>
          ) : (
            <ul className="grid gap-3 p-4 md:grid-cols-2">
              {friends.map((friend) => {
                const assets = resolveChatAvatarAssets(friend.user.avatar_key)
                const label = getUserDisplayName(friend.user)
                return (
                  <li
                    key={friend.user.id}
                    className="flex items-center gap-3 border border-zinc-800 bg-black px-3 py-3"
                  >
                    <img
                      src={assets.avatar}
                      alt=""
                      className="h-12 w-12 shrink-0 object-cover"
                      loading="lazy"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-semibold text-zinc-100">
                        {label}
                      </div>
                      <div className="truncate text-xs text-zinc-500">
                        @{friend.user.username}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/private-chat/${friend.user.id}`)
                      }
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

        <section className="rounded-sm border border-zinc-800 bg-zinc-950/40">
          <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold text-white">
            添加好友
          </h2>
          <form onSubmit={findUser} className="flex flex-wrap gap-2 p-4">
            <label htmlFor="friend-username" className="sr-only">
              要添加的好友用户名
            </label>
            <input
              id="friend-username"
              type="text"
              autoComplete="username"
              disabled={lookupLoading || requestLoading}
              value={username}
              onChange={(event) => {
                setUsername(event.target.value)
                setMatchedUser(null)
              }}
              placeholder="输入完整用户名"
              className="min-w-0 flex-1 border border-zinc-700 bg-black px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={lookupLoading || requestLoading}
              className="border border-zinc-700 px-3 py-2 text-sm transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
            >
              {lookupLoading ? '查找中...' : '查找用户'}
            </button>
            {matchedUser && (
              <div
                aria-live="polite"
                className="flex w-full flex-wrap items-center justify-between gap-3 border border-zinc-800 px-3 py-3"
              >
                <span className="text-sm text-zinc-200">
                  {getUserDisplayName(matchedUser)} (@{matchedUser.username})
                </span>
                <button
                  type="button"
                  disabled={requestLoading}
                  onClick={() => void sendFriendRequest()}
                  className="border border-cyan-800 px-3 py-1.5 text-xs text-cyan-200 transition hover:border-cyan-500 disabled:cursor-not-allowed disabled:text-zinc-600"
                >
                  {requestLoading ? '发送中...' : '发送好友申请'}
                </button>
              </div>
            )}
          </form>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-sm border border-zinc-800 bg-zinc-950/40">
            <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold text-white">
              收到的申请
            </h2>
            {loadError ? (
              <p className="px-4 py-6 text-sm text-zinc-500">
                好友申请暂不可用。
              </p>
            ) : incomingFriendRequests.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-500">
                暂无收到的好友申请。
              </p>
            ) : (
              <ul className="divide-y divide-zinc-800">
                {incomingFriendRequests.map((request) => (
                  <li
                    key={request.id}
                    className="flex items-center justify-between gap-3 px-4 py-3"
                  >
                    <span className="min-w-0 truncate text-sm text-zinc-200">
                      {requestName(request, 'requester')}
                    </span>
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
            <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold text-white">
              发出的申请
            </h2>
            {loadError ? (
              <p className="px-4 py-6 text-sm text-zinc-500">
                好友申请暂不可用。
              </p>
            ) : outgoingFriendRequests.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-500">
                暂无发出的好友申请。
              </p>
            ) : (
              <ul className="divide-y divide-zinc-800">
                {outgoingFriendRequests.map((request) => (
                  <li
                    key={request.id}
                    className="flex items-center justify-between gap-3 px-4 py-3"
                  >
                    <span className="min-w-0 truncate text-sm text-zinc-200">
                      {requestName(request, 'recipient')}
                    </span>
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
