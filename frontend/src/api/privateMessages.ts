import { apiClient } from './client'
import type { PaginatedPrivateMessagesResponse } from '@/types/chat'

export const privateMessagesApi = {
  getPageByFriend: async (
    friendId: number,
    params?: { limit?: number; beforeId?: number | null },
  ): Promise<PaginatedPrivateMessagesResponse> => {
    const { data } = await apiClient.get<PaginatedPrivateMessagesResponse>(`/private-messages/${friendId}`, {
      params: { limit: params?.limit, before_id: params?.beforeId },
    })
    return data
  },
}
