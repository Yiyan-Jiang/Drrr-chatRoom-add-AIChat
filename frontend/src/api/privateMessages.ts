/** 查询当前用户与指定好友的私聊历史分页。 */
import { apiClient } from './client'
import type { PaginatedPrivateMessagesResponse } from '@/types/privateMessages'

/** 私聊历史查询接口。 */
export const privateMessagesApi = {
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
