/**
 * 展示旧版聊天消息列表并自动滚动到底部。
 */
import { useEffect, useRef } from 'react'
import type { Message } from '@/types/chat'
import ChatMessage from '@/components/chat/ChatMessage'

/** 旧版消息列表的数据与当前用户标识。 */
interface ChatMessageListProps {
  /** 按展示顺序提供的消息列表。 */
  messages: Message[]
  /** 当前用户 ID，用于识别本人消息。 */
  currentUserId?: number
}

/** 按传入顺序展示旧版消息列表，并在 messages 变化后滚动到底部。 */
export default function ChatMessageList({
  messages,
  currentUserId,
}: ChatMessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-gray-500">
        <div className="text-center">
          <div className="mb-4 text-4xl">💬</div>
          <p>还没有消息</p>
          <p className="text-sm">发送第一条消息开始聊天吧</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <ChatMessage
          key={msg.id}
          message={msg}
          isOwn={msg.user_id === currentUserId}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}
