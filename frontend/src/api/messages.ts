import { apiClient } from "./client";
import type { Message, PaginatedMessagesResponse } from "../types/chat";

export interface CreateMessageRequest {
  content: string ;
  room_id: number ;
  client_message_id?: string | null;
}

export const messagesApi = {
  // 创建消息
  create: async (data: CreateMessageRequest): Promise<Message> => {
    const { data: message } = await apiClient.post<Message>('/messages/', data)
    return message
  },

  // 获取某个房间最近消息
  getByRoom: async (
    roomId: number,
    params: { limit?: number; beforeId?: number | null } = {},
  ): Promise<Message[]> => {
    const { data } = await apiClient.get<Message[]>(`/messages/room/${roomId}`, {
      params: {
        limit: params.limit,
        before_id: params.beforeId ?? undefined,
      },
    })
    return data
  },

  getPageByRoom: async (
    roomId: number,
    params: { limit?: number; beforeId?: number | null } = {},
  ): Promise<PaginatedMessagesResponse> => {
    const { data } = await apiClient.get<PaginatedMessagesResponse>(`/messages/room/${roomId}/page`, {
      params: {
        limit: params.limit,
        before_id: params.beforeId ?? undefined,
      },
    })
    return data
  },

  // 获取单条消息
  getById: async (messageId: number): Promise<Message> => {
    const { data } = await apiClient.get<Message>(`/messages/${messageId}`)
    return data
  },

  // 删除消息
  delete: async (messageId: number): Promise<void> => {
    await apiClient.delete(`/messages/${messageId}`)
  }


}
