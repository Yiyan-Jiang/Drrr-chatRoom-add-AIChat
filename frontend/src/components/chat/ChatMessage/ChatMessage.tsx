/**
 * 展示旧版普通聊天消息气泡。
 */
import type { Message } from '@/types/chat'

/** 旧版消息气泡的内容与归属。 */
interface ChatMessageProps {
  /** 待展示的消息。 */
  message: Message
  /** 是否为当前用户的消息，控制左右布局。 */
  isOwn: boolean
  /** 对方显示名，缺省时根据用户 ID 生成名称。 */
  username?: string
}

/** 按消息归属排列旧版消息气泡，展示发送时间与对方名称。 */
export default function ChatMessage({
  message,
  isOwn,
  username,
}: ChatMessageProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })
  }

  const displayName = isOwn ? '你' : username || `用户${message.user_id}`
  const avatarEmoji = '👤'

  if (isOwn) {
    return (
      <div className="flex justify-end">
        <div className="flex gap-2 max-w-[80%]">
          <div className="flex flex-col items-end gap-1">
            <div className="rounded-2xl rounded-br-none bg-blue-600 text-white px-4 py-3">
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className="mt-1 text-right text-xs opacity-70">
                {formatTime(message.created_at)}
              </div>
            </div>
          </div>
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm">
            {avatarEmoji}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="flex gap-2 max-w-[80%]">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm">
          {avatarEmoji}
        </div>
        <div className="flex flex-col gap-1">
          <div className="text-xs font-medium text-gray-400">{displayName}</div>
          <div className="rounded-2xl rounded-bl-none bg-gray-800 text-gray-100 px-4 py-3">
            <div className="whitespace-pre-wrap">{message.content}</div>
            <div className="mt-1 text-xs text-gray-500">
              {formatTime(message.created_at)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
