/** 在重连后回补聊天历史，并合并消息和历史分页游标。 */
import type { Message, PaginatedMessagesResponse } from '@/types/chat'
import { MAX_LOADED_MESSAGES, mergeMessages } from './chatMessageMerge'

/**
 * 向更早消息翻页，直到覆盖断连前的消息编号或到达历史末尾。
 * @param fetchPage - 按更早消息游标查询一页历史。
 * @param lastMessageId - 断连前已知的最新服务端消息编号；0 表示没有已知消息。
 * @param onPage - 回补结束后接收累计消息与末页分页信息的回调。
 * @param isActive - 查询仍属于当前会话时返回 true。
 * @returns 回补完成或当前会话失效后结束的 Promise。
 * @throws 查询失败或历史游标未向前推进时抛出错误。
 */
export async function recoverChatHistory<
  T extends {
    /** 用于判断历史是否覆盖断连前进度的服务端消息编号。 */ id: number
  },
>(
  fetchPage: (beforeId: number | null) => Promise<{
    /** 当前历史页或累计回补的消息。 */ items: T[]
    /** 是否仍有更早的历史消息。 */ has_more: boolean
    /** 继续查询更早消息使用的编号游标。 */ next_before_id: number | null
  }>,
  lastMessageId: number,
  onPage: (page: {
    /** 当前历史页或累计回补的消息。 */ items: T[]
    /** 是否仍有更早的历史消息。 */ has_more: boolean
    /** 继续查询更早消息使用的编号游标。 */ next_before_id: number | null
  }) => void,
  isActive: () => boolean,
) {
  let beforeId: number | null = null
  let items: T[] = []
  while (isActive()) {
    const page = await fetchPage(beforeId)
    if (!isActive()) return
    items = [...items, ...page.items].slice(0, MAX_LOADED_MESSAGES)
    if (
      !lastMessageId ||
      page.items.some((message) => message.id <= lastMessageId) ||
      !page.has_more ||
      page.next_before_id === null
    ) {
      onPage({ ...page, items })
      return
    }
    if (beforeId !== null && page.next_before_id >= beforeId)
      throw new Error('History cursor did not advance')
    beforeId = page.next_before_id
  }
}

/**
 * 将重连回补消息合并到现有历史，并重新计算被裁剪后的分页状态。
 * @param state - 已加载消息和现有分页状态。
 * @param page - 重连回补得到的历史页。
 * @returns 合并后的消息、是否还有历史及下一页游标。
 */
export function mergeRecoveredHistory(
  state: {
    /** 回补前已载入的消息。 */ messages: Message[]
    /** 回补前是否仍有更早的历史消息。 */ hasMore: boolean
    /** 回补前加载更早消息使用的编号游标。 */ nextBeforeId: number | null
  },
  page: PaginatedMessagesResponse,
) {
  const messages = mergeMessages(state.messages, page.items, 'head')
  const oldestId = (items: Message[]) =>
    Math.min(
      ...items.filter((message) => message.id > 0).map((message) => message.id),
    )
  const previousOldest = oldestId(state.messages)
  const currentOldest = oldestId(messages)
  const historyExpanded = oldestId(page.items) <= previousOldest
  const historyTrimmed = currentOldest > previousOldest
  const hasMore =
    historyTrimmed || (historyExpanded ? page.has_more : state.hasMore)
  return {
    messages,
    hasMore,
    nextBeforeId: !hasMore
      ? null
      : historyExpanded || historyTrimmed
        ? Number.isFinite(currentOldest)
          ? currentOldest
          : page.next_before_id
        : state.nextBeforeId,
  }
}
