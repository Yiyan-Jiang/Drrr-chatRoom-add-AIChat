/**
 * @parm 组件用途：承载聊天室消息滚动区和新消息跳转入口。
 */
import type { RefObject } from 'react'
import type { Message } from '@/types/chat'
import ChatMessageItem from '@/components/chat/ChatMessageItem'
import SystemMessageItem from '@/components/chat/SystemMessageItem'

interface ChatMessageViewportProps {
  messages: Message[]
  currentUserId?: number
  hasMore: boolean
  loadingOlder: boolean
  unreadNewCount: number
  containerRef: RefObject<HTMLDivElement | null>
  onScroll: () => void
  onJumpToHead: () => void
}

export default function ChatMessageViewport({
  messages,
  currentUserId,
  hasMore,
  loadingOlder,
  unreadNewCount,
  containerRef,
  onScroll,
  onJumpToHead,
}: ChatMessageViewportProps) {
  return (
    <div className="relative flex min-h-0 flex-1 bg-black">
      <div
        ref={containerRef}
        onScroll={onScroll}
        className="h-full w-full overflow-y-auto px-4 py-4"
      >
        <div className="mx-auto flex max-w-5xl flex-col gap-4">
          {messages.map((message) =>
            message.message_type === 'system' ? (
              <SystemMessageItem key={message.id} message={message} />
            ) : (
              <ChatMessageItem
                key={message.id > 0 ? message.id : message.client_message_id || message.id}
                message={message}
                isOwn={message.user_id === currentUserId}
              />
            ),
          )}
          <div className="py-3 text-center text-xs text-zinc-500">
            {loadingOlder ? '加载历史消息...' : hasMore ? '向下滚动加载历史消息' : '没有更多消息'}
          </div>
        </div>
      </div>
      {unreadNewCount > 0 ? (
        <button
          type="button"
          onClick={onJumpToHead}
          className="absolute left-1/2 top-3 -translate-x-1/2 rounded-full bg-cyan-500 px-3 py-1 text-xs font-semibold text-black shadow"
        >
          {unreadNewCount} 条新消息
        </button>
      ) : null}
    </div>
  )
}
