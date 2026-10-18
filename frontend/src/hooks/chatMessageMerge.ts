/** 按服务端编号和客户端关联编号合并聊天消息，并创建待发送消息。 */
import type { Message } from '@/types/chat'

/** 单个聊天会话在前端保留的消息数量上限。 */
export const MAX_LOADED_MESSAGES = 300

/**
 * 复制消息，并为缺省的消息类型和发送状态补入 user 与 sent。
 * @param message - 待参与合并的消息。
 * @returns 已补齐展示状态的消息副本。
 */
function normalizeMessage(message: Message): Message {
  return {
    ...message,
    message_type: message.message_type ?? 'user',
    delivery_status: message.delivery_status ?? 'sent',
  }
}

/**
 * 优先按客户端关联编号、再按服务端编号覆盖重复消息，按时间倒序保留最近 300 条。
 * @param existing - 当前已加载的消息。
 * @param incoming - 本次收到的历史、事件或发送回执。
 * @param mode - 去重后新记录拼接到现有数组的方向；最终仍按时间排序。
 * @returns 合并、排序并裁剪后的新数组。
 */
export function mergeMessages(
  existing: Message[],
  incoming: Message[],
  mode: 'head' | 'tail',
) {
  const byId = new Map<number, number>()
  const byClientId = new Map<string, number>()
  const merged = existing.map((message, index) => {
    if (message.id > 0) byId.set(message.id, index)
    if (message.client_message_id)
      byClientId.set(message.client_message_id, index)
    return normalizeMessage(message)
  })

  const append: Message[] = []
  for (const raw of incoming) {
    const message = normalizeMessage(raw)
    const existingIndex =
      message.client_message_id && byClientId.has(message.client_message_id)
        ? byClientId.get(message.client_message_id)
        : message.id > 0
          ? byId.get(message.id)
          : undefined

    if (existingIndex !== undefined) {
      const target = existingIndex < merged.length ? merged : append
      const index =
        existingIndex < merged.length
          ? existingIndex
          : existingIndex - merged.length
      target[index] = {
        ...target[index],
        ...message,
        delivery_status: message.delivery_status ?? 'sent',
      }
      if (message.id > 0) byId.set(message.id, existingIndex)
      continue
    }

    const index = merged.length + append.length
    if (message.id > 0) byId.set(message.id, index)
    if (message.client_message_id)
      byClientId.set(message.client_message_id, index)
    append.push(message)
  }

  const result =
    mode === 'head' ? [...append, ...merged] : [...merged, ...append]
  return result
    .sort((a, b) => {
      const created =
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      return created || b.id - a.id
    })
    .slice(0, MAX_LOADED_MESSAGES)
}

/**
 * 创建本地发送中的消息，使用负时间戳编号等待服务端回执合并。
 * @param params - 房间、发送者、正文和客户端关联编号。
 * @returns 带有当前时间与 sending 状态的本地消息。
 */
export function createOptimisticMessage(params: {
  /** 消息所属房间编号；私聊调用方传入 0。 */
  roomId: number
  /** 当前消息发送方用户编号。 */
  userId: number
  /** 准备发送的消息正文。 */
  content: string
  /** 用于匹配服务端回执的客户端关联编号。 */
  clientMessageId: string
  /** 用于立即显示本地消息的发送者资料。 */
  author?: Message['author']
}): Message {
  return {
    id: -Date.now(),
    room_id: params.roomId,
    user_id: params.userId,
    content: params.content,
    client_message_id: params.clientMessageId,
    message_type: 'user',
    author: params.author,
    created_at: new Date().toISOString(),
    delivery_status: 'sending',
  }
}
