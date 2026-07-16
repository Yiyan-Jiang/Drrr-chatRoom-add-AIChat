/**
 * 私聊消息类型：服务一对一聊天历史、私聊 Socket.IO 消息和私聊 API。
 */
import type { Message } from './chat'

export interface PrivateMessage extends Message {
  sender_id: number
  recipient_id: number
}

export interface PaginatedPrivateMessagesResponse {
  items: PrivateMessage[]
  has_more: boolean
  next_before_id: number | null
}
