/** 查询当前用户与指定好友的私聊历史分页。 */
import { apiClient } from './client'
import type {
  PaginatedPrivateConversationsResponse,
  PaginatedPrivateMessagesResponse,
} from '@/types/privateMessages'

/** 私聊历史查询接口。 */
export const privateMessagesApi = {
  /**
   * 查询当前用户的私聊会话分页。
   * @param params - 会话页码和每页数量。
   * @returns 包含最近消息及未读数的会话摘要。
   */
  getConversations: async (params?: {
    /** 要查询的会话页码。 */ page?: number
    /** 每页最多返回的会话数量。 */ pageSize?: number
  }): Promise<PaginatedPrivateConversationsResponse> => {
    const { data } = await apiClient.get<PaginatedPrivateConversationsResponse>(
      '/private-messages/conversations',
      {
        params: { page: params?.page, page_size: params?.pageSize },
      },
    )
    return data
  },

  /**
   * 持久化当前用户已读取的指定好友消息边界。
   * @param friendId - 消息发送方用户编号。
   * @param throughId - 已加载的接收消息编号边界。
   * @returns 更新完成后结束的 Promise。
   */
  markRead: async (friendId: number, throughId: number): Promise<void> => {
    await apiClient.put(`/private-messages/${friendId}/read`, {
      through_id: throughId,
    })
  },

  /**
   * 查询当前用户与指定好友的私聊历史。
   * @param friendId - 好友用户编号。
   * @param params - 数量上限和更早消息编号游标。
   * @returns 私聊消息及后续历史游标。
   */
  getPageByFriend: async (
    friendId: number,
    params?: {
      /** 本次最多返回的私聊消息数量。 */ limit?: number
      /** 只查询此消息编号之前的私聊历史；省略时从最新消息开始。 */ beforeId?:
        number | null
    },
  ): Promise<PaginatedPrivateMessagesResponse> => {
    const { data } = await apiClient.get<PaginatedPrivateMessagesResponse>(
      `/private-messages/${friendId}`,
      {
        params: { limit: params?.limit, before_id: params?.beforeId },
      },
    )
    return data
  },
}
