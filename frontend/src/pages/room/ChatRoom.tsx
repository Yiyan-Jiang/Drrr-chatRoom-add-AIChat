import { useCallback, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '@/contexts/AuthContext'
import { useChatScroll } from '@/hooks/useChatScroll'
import { useRoomChat } from '@/hooks/useRoomChat'
import ChatMessageViewport from '@/components/chat/ChatMessageViewport'
import ChatRoomHeader from '@/components/chat/ChatRoomHeader'
import RoomInfoDrawer from '@/components/chat/RoomInfoDrawer'
import PageState from '@/components/common/PageState'

export default function ChatRoom() {
  const { roomId } = useParams<{ roomId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [roomInfoOpen, setRoomInfoOpen] = useState(false)
  const roomIdNum = useMemo(() => Number.parseInt(roomId || '0', 10), [roomId])

  const { containerRef, handleScroll, isNearHead, scrollToHead } = useChatScroll()
  const chat = useRoomChat(roomIdNum, user, isNearHead, scrollToHead)
  const { refreshRoom } = chat

  const openRoomInfo = useCallback(() => {
    refreshRoom().then(() => {
      setRoomInfoOpen(true)
    }).catch((error) => {
      if (error?.kind === 'not_found') {
        setRoomInfoOpen(false)
        toast.error('房间不存在或已被删除')
        navigate('/home/rooms')
        return
      }
      if (error?.kind !== 'forbidden') {
        toast.error(error?.message || '刷新房间信息失败')
      }
    })
  }, [navigate, refreshRoom])

  if (!roomIdNum || Number.isNaN(roomIdNum)) {
    toast.error('无效的房间ID')
    navigate('/home/rooms')
    return null
  }

  if (chat.initialLoading) {
    return <PageState>加载房间信息...</PageState>
  }

  if (chat.error?.kind === 'not_found' || !chat.room) {
    return <PageState>{chat.error?.message || '房间不存在'}</PageState>
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-black">
      <ChatRoomHeader
        roomName={chat.room.name}
        roomId={chat.room.id}
        composerValue={chat.composerValue}
        reconnecting={chat.reconnecting}
        onComposerChange={chat.setComposerValue}
        onSubmit={chat.sendMessage}
        onLeaveRoom={() => navigate('/home/rooms')}
        onOpenInfo={openRoomInfo}
      />
      <ChatMessageViewport
        messages={chat.messages}
        currentUserId={user?.id}
        hasMore={chat.hasMore}
        loadingOlder={chat.loadingOlder}
        unreadNewCount={chat.unreadNewCount}
        containerRef={containerRef}
        onScroll={() => handleScroll(chat.loadOlderMessages)}
        onJumpToHead={() => {
          scrollToHead()
          chat.clearUnread()
        }}
      />
      <RoomInfoDrawer
        open={roomInfoOpen}
        room={chat.room}
        members={chat.members}
        currentUserId={user?.id}
        deletingRoom={chat.deletingRoom}
        updatingRoom={chat.updatingRoom}
        onClose={() => setRoomInfoOpen(false)}
        onDeleteRoom={async () => {
          await chat.deleteRoom()
          navigate('/home/rooms')
        }}
        onUpdateRoom={chat.updateRoom}
      />
    </div>
  )
}
