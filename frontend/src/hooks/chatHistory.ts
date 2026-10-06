import type { Message, PaginatedMessagesResponse } from '@/types/chat'
import { MAX_LOADED_MESSAGES, mergeMessages } from './chatMessageMerge'

export async function recoverChatHistory<T extends { id: number }>(
  fetchPage: (beforeId: number | null) => Promise<{ items: T[]; has_more: boolean; next_before_id: number | null }>,
  lastMessageId: number,
  onPage: (page: { items: T[]; has_more: boolean; next_before_id: number | null }) => void,
  isActive: () => boolean,
) {
  let beforeId: number | null = null
  let items: T[] = []
  while (isActive()) {
    const page = await fetchPage(beforeId)
    if (!isActive()) return
    items = [...items, ...page.items].slice(0, MAX_LOADED_MESSAGES)
    if (!lastMessageId || page.items.some((message) => message.id <= lastMessageId) || !page.has_more || page.next_before_id === null) {
      onPage({ ...page, items })
      return
    }
    if (beforeId !== null && page.next_before_id >= beforeId) throw new Error('History cursor did not advance')
    beforeId = page.next_before_id
  }
}

export function mergeRecoveredHistory(
  state: { messages: Message[]; hasMore: boolean; nextBeforeId: number | null },
  page: PaginatedMessagesResponse,
) {
  const messages = mergeMessages(state.messages, page.items, 'head')
  const oldestId = (items: Message[]) => Math.min(...items.filter((message) => message.id > 0).map((message) => message.id))
  const previousOldest = oldestId(state.messages)
  const currentOldest = oldestId(messages)
  const historyExpanded = oldestId(page.items) <= previousOldest
  const historyTrimmed = currentOldest > previousOldest
  const hasMore = historyTrimmed || (historyExpanded ? page.has_more : state.hasMore)
  return {
    messages,
    hasMore,
    nextBeforeId: !hasMore ? null : historyExpanded || historyTrimmed
      ? Number.isFinite(currentOldest) ? currentOldest : page.next_before_id
      : state.nextBeforeId,
  }
}
