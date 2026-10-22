/** 定义私聊消息和私聊历史分页响应。 */
import type { Message } from './chat'
import type { User } from './user'

/** 包含明确发送方和接收方的私聊消息。 */
export interface PrivateMessage extends Message {
  /** 发送方用户编号。 */
  sender_id: number
  /** 接收方用户编号。 */
  recipient_id: number
}

/** 按消息编号向前翻页的私聊历史。 */
export interface PaginatedPrivateMessagesResponse {
  /** 当前页记录。 */
  items: PrivateMessage[]
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
  /** 下一页查询使用的更早消息编号游标。 */
  next_before_id: number | null
}

/** 邮箱中的私聊会话摘要及当前用户的未读数量。 */
export interface PrivateConversation {
  /** 会话中的另一位用户。 */
  user: User
  /** 会话中最近的一条消息。 */
  latest_message: PrivateMessage
  /** 当前用户尚未读取的接收消息数量。 */
  unread_count: number
}

/** 邮箱会话分页结果。 */
export interface PaginatedPrivateConversationsResponse {
  /** 按最近消息时间排列的会话摘要。 */
  items: PrivateConversation[]
  /** 服务端是否还有下一页会话。 */
  has_more: boolean
}
