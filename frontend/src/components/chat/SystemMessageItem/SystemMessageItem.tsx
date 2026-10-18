/**
 * 展示聊天室系统消息。
 */
import type { Message } from '@/types/chat'

/** 系统消息展示数据。 */
interface SystemMessageItemProps {
  /** 正文作为居中提示展示的消息。 */
  message: Message
}

/** 以居中提示样式展示系统消息正文。 */
export default function SystemMessageItem({ message }: SystemMessageItemProps) {
  return (
    <div className="py-1 text-center text-xs text-zinc-500">
      {message.content}
    </div>
  )
}
