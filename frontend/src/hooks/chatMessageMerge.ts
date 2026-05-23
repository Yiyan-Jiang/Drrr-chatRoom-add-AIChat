import type { Message } from '@/types/chat'

const MAX_LOADED_MESSAGES = 300

function normalizeMessage(message: Message): Message {
  return {
    ...message,
    message_type: message.message_type ?? 'user',
    delivery_status: message.delivery_status ?? 'sent',
  }
}

export function mergeMessages(existing: Message[], incoming: Message[], mode: 'head' | 'tail') {
  const byId = new Map<number, number>()
  const byClientId = new Map<string, number>()
  const merged = existing.map((message, index) => {
    if (message.id > 0) byId.set(message.id, index)
    if (message.client_message_id) byClientId.set(message.client_message_id, index)
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
      merged[existingIndex] = {
        ...merged[existingIndex],
        ...message,
        delivery_status: message.delivery_status ?? 'sent',
      }
      continue
    }

    append.push(message)
  }

  const result = mode === 'head' ? [...append, ...merged] : [...merged, ...append]
  return result
    .sort((a, b) => {
      const created = new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      return created || b.id - a.id
    })
    .slice(0, MAX_LOADED_MESSAGES)
}

export function createOptimisticMessage(params: {
  roomId: number
  userId: number
  content: string
  clientMessageId: string
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
