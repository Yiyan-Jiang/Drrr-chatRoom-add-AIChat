import { useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useChatScroll } from '@/hooks/useChatScroll'
import { usePrivateChat } from '@/hooks/usePrivateChat'
import ChatMessageViewport from '@/components/chat/ChatMessageViewport'
import ChatRoomHeader from '@/components/chat/ChatRoomHeader'
import PageState from '@/components/common/PageState'
import { getUserDisplayName } from '@/utils/userDisplayName'

export default function PrivateChat() {
  const { friendId } = useParams<{ friendId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const friendIdNum = useMemo(() => Number.parseInt(friendId || '0', 10), [friendId])
  const { containerRef, handleScroll, isNearHead, scrollToHead } = useChatScroll()
  const chat = usePrivateChat(friendIdNum, user, isNearHead, scrollToHead)

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
        onLeaveRoom={() => navigate('/home/rooms')}
        onOpenInfo={() => navigate('/my')}
      />
      <ChatMessageViewport
        messages={chat.messages}
        currentUserId={user?.id}
        hasMore={chat.hasMore}
        loadingOlder={chat.loadingOlder}
        unreadNewCount={0}
        containerRef={containerRef}
        onScroll={() => handleScroll(chat.loadOlderMessages)}
        onJumpToHead={() => scrollToHead()}
      />
    </div>
  )
}
