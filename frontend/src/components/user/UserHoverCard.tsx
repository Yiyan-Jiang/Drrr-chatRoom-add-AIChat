import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { friendsApi } from '@/api/friends'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { useAuth } from '@/contexts/AuthContext'
import type { FriendRequest } from '@/types/friends'
import type { User } from '@/types/user'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { logger } from '@/utils/logger'

type FriendRelation = 'self' | 'friend' | 'outgoing' | 'incoming' | 'none'

interface UserHoverCardProps {
  user: User | null
  align?: 'left' | 'right'
  avatarClassName?: string
  nameClassName?: string
  showName?: boolean
}

function findRequest(requests: FriendRequest[], userId: number, currentUserId: number, incoming: boolean) {
  return requests.find((request) =>
    incoming
      ? request.requester.id === userId && request.recipient.id === currentUserId && request.status === 'pending'
      : request.requester.id === currentUserId && request.recipient.id === userId && request.status === 'pending',
  )
}

export default function UserHoverCard({
  user,
  align = 'left',
  avatarClassName = 'h-11 w-11',
  nameClassName = 'max-w-12 text-white',
  showName = true,
}: UserHoverCardProps) {
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const [open, setOpen] = useState(false)
  const [relation, setRelation] = useState<FriendRelation>('none')
  const [incomingRequest, setIncomingRequest] = useState<FriendRequest | null>(null)
  const [busy, setBusy] = useState(false)
  const assets = resolveChatAvatarAssets(user?.avatar_key)
  const displayName = getUserDisplayName(user, user?.id ? `用户${user.id}` : '系统')
  const isSelf = !!user && !!currentUser && user.id === currentUser.id

  useEffect(() => {
    if (!open || !user || !currentUser) return
    if (isSelf) {
      return
    }
    const targetUser = user
    const viewer = currentUser
    let cancelled = false
    async function loadRelation() {
      try {
        const [friends, incoming, outgoing] = await Promise.all([
          friendsApi.listFriends({ page: 1, pageSize: 50 }),
          friendsApi.listRequests('incoming'),
          friendsApi.listRequests('outgoing'),
        ])
        if (cancelled) return
        if (friends.items.some((friend) => friend.user.id === targetUser.id)) {
          setRelation('friend')
          setIncomingRequest(null)
          return
        }
        const incomingPending = findRequest(incoming.items, targetUser.id, viewer.id, true)
        if (incomingPending) {
          setRelation('incoming')
          setIncomingRequest(incomingPending)
          return
        }
        if (findRequest(outgoing.items, targetUser.id, viewer.id, false)) {
          setRelation('outgoing')
          setIncomingRequest(null)
          return
        }
        setRelation('none')
        setIncomingRequest(null)
      } catch (error) {
        logger.error('[user-hover-card] failed to load friend relation', {
          message: error instanceof Error ? error.message : String(error),
        })
      }
    }
    loadRelation()
    return () => {
      cancelled = true
    }
  }, [currentUser, isSelf, open, user])

  const actionLabel = useMemo(() => {
    if (!user) return '不可用'
    if (isSelf || relation === 'self') return '这是你'
    if (relation === 'friend') return '发起私聊'
    if (relation === 'outgoing') return '已申请'
    if (relation === 'incoming') return '接受申请'
    return '申请好友'
  }, [isSelf, relation, user])

  const handleAction = async () => {
    if (!user || !currentUser || isSelf || relation === 'self' || relation === 'outgoing' || busy) return
    if (relation === 'friend') {
      navigate(`/private-chat/${user.id}`)
      return
    }
    setBusy(true)
    try {
      if (relation === 'incoming' && incomingRequest) {
        await friendsApi.acceptRequest(incomingRequest.id)
        setRelation('friend')
        toast.success('已成为好友')
      } else {
        await friendsApi.createRequest({ recipient_id: user.id })
        setRelation('outgoing')
        toast.success('好友申请已发送')
      }
    } catch (error) {
      logger.error('[user-hover-card] friend action failed', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('操作失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="relative flex flex-none flex-col items-center gap-1">
      <button
        type="button"
        onClick={(event) => {
          event.preventDefault()
          event.stopPropagation()
          setOpen((value) => !value)
        }}
        className={`${avatarClassName} block overflow-hidden rounded outline-none ring-offset-2 ring-offset-black transition hover:ring-2 hover:ring-zinc-500 focus-visible:ring-2 focus-visible:ring-cyan-400`}
        aria-label="查看用户资料"
        aria-expanded={open}
      >
        <img src={assets.avatar} alt="" className="h-full w-full object-cover" loading="lazy" />
      </button>
      {showName ? <div className={`${nameClassName} truncate text-center text-xs`}>{displayName}</div> : null}

      {open && (
        <div
          role="dialog"
          aria-label="用户资料"
          className={`absolute top-[calc(100%+0.5rem)] z-30 w-64 rounded border border-zinc-800 bg-zinc-950 p-4 text-left shadow-2xl shadow-black/60 ${
            align === 'right' ? 'right-0' : 'left-0'
          }`}
          onClick={(event) => {
            event.preventDefault()
            event.stopPropagation()
          }}
        >
          {user ? (
            <>
              <div className="flex items-start gap-3">
                <img src={assets.avatar} alt="" className="h-14 w-14 shrink-0 rounded object-cover" loading="lazy" />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-semibold text-zinc-100">{user.username}</div>
                  <div className="mt-0.5 truncate text-xs text-zinc-400">{user.nickname?.trim() || '暂无昵称'}</div>
                  <div className="mt-3 text-xs leading-relaxed text-zinc-300">{user.bio?.trim() || '暂无简介'}</div>
                </div>
              </div>
              <button
                type="button"
                disabled={busy || isSelf || relation === 'self' || relation === 'outgoing'}
                onClick={handleAction}
                className="mt-4 h-8 w-full rounded border border-zinc-700 text-xs text-zinc-100 transition hover:border-cyan-400 disabled:cursor-not-allowed disabled:text-zinc-500"
              >
                {busy ? '处理中...' : actionLabel}
              </button>
            </>
          ) : (
            <div className="text-sm text-zinc-400">用户信息不可用</div>
          )}
        </div>
      )}
    </div>
  )
}
