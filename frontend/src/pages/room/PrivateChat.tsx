/** 按路由好友 ID 连接私聊状态，组合消息区、发送区与返回入口。 */
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useChatScroll } from '@/hooks/useChatScroll'
import { usePrivateChat } from '@/hooks/usePrivateChat'
import ChatMessageViewport from '@/components/chat/ChatMessageViewport'
import ChatRoomHeader from '@/components/chat/ChatRoomHeader'
import PageState from '@/components/common/PageState'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { privateMessagesApi } from '@/api/privateMessages'
import { logger } from '@/utils/logger'

/** 按路由好友 ID 连接私聊状态，组合消息区、发送区与返回入口。 */
export default function PrivateChat() {
  const { friendId } = useParams<{ friendId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const friendIdNum = useMemo(
    () => Number.parseInt(friendId || '0', 10),
    [friendId],
  )
  const { containerRef, handleScroll, isNearHead, scrollToHead } =
    useChatScroll()
  const chat = usePrivateChat(friendIdNum, user, isNearHead, scrollToHead)
  const [readCheckVersion, setReadCheckVersion] = useState(0)
  const [readFailure, setReadFailure] = useState<{
    /** 已读更新失败的好友编号。 */
    friendId: number
    /** 已读更新失败的接收消息边界。 */
    throughId: number
    /** 展示给用户的已读同步错误。 */
    message: string
  } | null>(null)
  const readTracking = useRef<{
    /** 当前跟踪已读状态的好友编号。 */
    friendId: number
    /** 最近一次尝试同步的接收消息编号。 */
    lastAttemptedReadId: number | null
    /** 最近成功同步的接收消息编号。 */
    lastMarkedReadId: number
    /** 用户请求重试的接收消息编号。 */
    retryRequestedReadId: number | null
  }>({
    friendId: friendIdNum,
    lastAttemptedReadId: null,
    lastMarkedReadId: 0,
    retryRequestedReadId: null,
  })

  useEffect(() => {
    const checkVisibility = () => setReadCheckVersion((version) => version + 1)
    document.addEventListener('visibilitychange', checkVisibility)
    return () =>
      document.removeEventListener('visibilitychange', checkVisibility)
  }, [])

  useEffect(() => {
    if (
      chat.initialLoading ||
      !user ||
      chat.friend?.id !== friendIdNum ||
      document.visibilityState !== 'visible' ||
      !isNearHead()
    )
      return

    const throughId = Math.max(
      0,
      ...chat.messages
        .filter(
          (message) =>
            message.id > 0 &&
            message.sender_id === friendIdNum &&
            message.recipient_id === user.id,
        )
        .map((message) => message.id),
    )
    if (readTracking.current.friendId !== friendIdNum) {
      readTracking.current = {
        friendId: friendIdNum,
        lastAttemptedReadId: null,
        lastMarkedReadId: 0,
        retryRequestedReadId: null,
      }
    }
    const tracking = readTracking.current
    if (
      throughId <= 0 ||
      throughId <= tracking.lastMarkedReadId ||
      (tracking.lastAttemptedReadId === throughId &&
        tracking.retryRequestedReadId !== throughId)
    )
      return

    tracking.lastAttemptedReadId = throughId
    tracking.retryRequestedReadId = null
    void privateMessagesApi
      .markRead(friendIdNum, throughId)
      .then(() => {
        if (readTracking.current !== tracking) return
        tracking.lastMarkedReadId = Math.max(
          tracking.lastMarkedReadId,
          throughId,
        )
        setReadFailure((failure) =>
          failure?.friendId === friendIdNum && failure.throughId <= throughId
            ? null
            : failure,
        )
      })
      .catch((error: unknown) => {
        if (
          readTracking.current !== tracking ||
          throughId <= tracking.lastMarkedReadId
        )
          return
        logger.error(
          '[private-chat] failed to mark received messages as read',
          {
            message: error instanceof Error ? error.message : String(error),
          },
        )
        setReadFailure((failure) =>
          failure?.friendId === friendIdNum && failure.throughId > throughId
            ? failure
            : {
                friendId: friendIdNum,
                throughId,
                message: '同步已读状态失败。',
              },
        )
      })
  }, [
    chat.friend?.id,
    chat.initialLoading,
    chat.messages,
    friendIdNum,
    isNearHead,
    readCheckVersion,
    user,
  ])

  if (!friendIdNum || Number.isNaN(friendIdNum)) {
    navigate('/home/rooms')
    return null
  }

  if (chat.initialLoading) {
    return <PageState>加载私聊...</PageState>
  }

  if (chat.error && !chat.friend) {
    return <PageState>{chat.error}</PageState>
  }

  const friendName = getUserDisplayName(chat.friend, `用户${friendIdNum}`)

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-black">
      <ChatRoomHeader
        roomName={friendName}
        roomId={friendIdNum}
        subtitle="private chat"
        composerValue={chat.composerValue}
        reconnecting={chat.reconnecting}
        infoLabel="资料"
        leaveLabel="退出"
        statusText={chat.error || undefined}
        onComposerChange={chat.setComposerValue}
        onSubmit={chat.sendMessage}
        onLeaveRoom={() => navigate('/friends/manage')}
        onOpenInfo={() => navigate('/my')}
      />
      <ChatMessageViewport
        messages={chat.messages}
        currentUserId={user?.id}
        hasMore={chat.hasMore}
        loadingOlder={chat.loadingOlder}
        unreadNewCount={0}
        containerRef={containerRef}
        onScroll={() => {
          setReadCheckVersion((version) => version + 1)
          handleScroll(chat.loadOlderMessages)
        }}
        onJumpToHead={() => scrollToHead()}
      />
      {readFailure?.friendId === friendIdNum ? (
        <div
          role="alert"
          className="flex items-center justify-center gap-3 border-t border-zinc-800 bg-black px-4 py-2 text-sm text-red-300"
        >
          <span>{readFailure.message}</span>
          <button
            type="button"
            onClick={() => {
              readTracking.current.retryRequestedReadId = readFailure.throughId
              setReadCheckVersion((version) => version + 1)
            }}
            className="border border-zinc-700 px-2 py-1 text-xs text-zinc-100 transition hover:border-cyan-500"
          >
            重试
          </button>
        </div>
      ) : null}
    </div>
  )
}
