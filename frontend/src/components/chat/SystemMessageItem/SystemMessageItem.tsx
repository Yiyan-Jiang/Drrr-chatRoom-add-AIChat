/**
 * @parm 组件用途：展示聊天室系统消息。
 */
import type { Message } from '@/types/chat'

interface SystemMessageItemProps {
  message: Message
}

export default function SystemMessageItem({ message }: SystemMessageItemProps) {
  return (
    <div className="py-1 text-center text-xs text-zinc-500">
      {message.content} 
    </div>
  )
}
