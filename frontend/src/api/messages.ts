/** 封装聊天室消息的创建、历史分页、详情查询和删除请求。 */
import { apiClient } from './client'
import type { Message, PaginatedMessagesResponse } from '../types/chat'

/** 向指定房间提交消息的请求。 */
export interface CreateMessageRequest {
  /** 聊天室消息正文。 */
  content: string
  /** 关联房间编号。 */
  room_id: number
  /** 关联本地待发送消息与服务端回执的编号。 */
  client_message_id?: string | null
}

/** 聊天室消息操作接口。 */
export const messagesApi = {
  /**
   * 通过 HTTP 创建聊天室消息。
   * @param data - 房间编号、正文和可选客户端关联编号。
   * @returns 服务端保存的消息。
   */
  create: async (data: CreateMessageRequest): Promise<Message> => {
    const { data: message } = await apiClient.post<Message>('/messages/', data)
    return message
  },
  /**
   * 查询指定房间的历史消息数组。
   * @param roomId - 房间编号。
   * @param params - 数量上限和更早消息编号游标。
   * @returns 历史消息数组。
   */
  getByRoom: async (
    roomId: number,
    params: {
      /** 本次最多返回的聊天室消息数量。 */ limit?: number
      /** 只查询此消息编号之前的历史；null 或省略时从最新消息开始。 */ beforeId?:
        number | null
    } = {},
  ): Promise<Message[]> => {
    const { data } = await apiClient.get<Message[]>(
      `/messages/room/${roomId}`,
      {
        params: {
          limit: params.limit,
          before_id: params.beforeId ?? undefined,
        },
      },
    )
    return data
  },

  /**
   * 查询指定房间的历史消息分页。
   * @param roomId - 房间编号。
   * @param params - 数量上限和更早消息编号游标。
   * @returns 消息及后续历史游标。
   */
  getPageByRoom: async (
    roomId: number,
    params: {
      /** 本次最多返回的聊天室消息数量。 */ limit?: number
      /** 只查询此消息编号之前的历史；null 或省略时从最新消息开始。 */ beforeId?:
        number | null
    } = {},
  ): Promise<PaginatedMessagesResponse> => {
    const { data } = await apiClient.get<PaginatedMessagesResponse>(
      `/messages/room/${roomId}/page`,
      {
        params: {
          limit: params.limit,
          before_id: params.beforeId ?? undefined,
        },
      },
    )
    return data
  },
  /**
   * 查询单条聊天室消息。
   * @param messageId - 消息编号。
   * @returns 消息详情。
   */
  getById: async (messageId: number): Promise<Message> => {
    const { data } = await apiClient.get<Message>(`/messages/${messageId}`)
    return data
  },
  /**
   * 删除指定聊天室消息。
   * @param messageId - 消息编号。
   * @returns 删除请求完成后结束的 Promise。
   */
  delete: async (messageId: number): Promise<void> => {
    await apiClient.delete(`/messages/${messageId}`)
  },
}
