/**
 * 承载聊天室消息滚动区和新消息跳转入口。
 */
import type { RefObject } from 'react'
import type { Message } from '@/types/chat'
import ChatMessageItem from '@/components/chat/ChatMessageItem'
import SystemMessageItem from '@/components/chat/SystemMessageItem'

/** 聊天滚动区数据、历史状态与滚动控制。 */
interface ChatMessageViewportProps {
  /** 按展示顺序提供的普通消息和系统消息。 */
  messages: Message[]
  /** 当前用户 ID，用于区分本人消息。 */
  currentUserId?: number
  /** 是否还有可加载的历史消息。 */
  hasMore: boolean
  /** 是否正在加载更早消息。 */
  loadingOlder: boolean
  /** 未跳转查看的新消息数量。 */
  unreadNewCount: number
  /** 滚动容器引用，由外部滚动逻辑维护。 */
  containerRef: RefObject<HTMLDivElement | null>
  /** 滚动容器触发滚动时调用。 */
  onScroll: () => void
  /** 请求跳转到列表头部的新消息区域。 */
  onJumpToHead: () => void
}

/** 按传入顺序渲染普通消息与系统消息，展示历史加载状态和新消息跳转按钮。 */
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
                key={
                  message.id > 0
                    ? message.id
                    : message.client_message_id || message.id
                }
                message={message}
                isOwn={message.user_id === currentUserId}
              />
            ),
          )}
          <div className="py-3 text-center text-xs text-zinc-500">
            {loadingOlder
              ? '加载历史消息...'
              : hasMore
                ? '向下滚动加载历史消息'
                : '没有更多消息'}
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
