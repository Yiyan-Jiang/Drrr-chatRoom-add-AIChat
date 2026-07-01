import { apiClient } from './client'
import type {
  CreateFriendRequest,
  FriendRequest,
  FriendRequestDirection,
  PaginatedFriendRequestsResponse,
  PaginatedFriendsResponse,
} from '@/types/chat'

export const friendsApi = {
  listFriends: async (params?: { page?: number; pageSize?: number }): Promise<PaginatedFriendsResponse> => {
    const { data } = await apiClient.get<PaginatedFriendsResponse>('/friends/', {
      params: { page: params?.page, page_size: params?.pageSize },
    })
    return data
  },

  createRequest: async (payload: CreateFriendRequest): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>('/friends/requests', payload)
    return data
  },

  listRequests: async (direction: FriendRequestDirection = 'all'): Promise<PaginatedFriendRequestsResponse> => {
    const { data } = await apiClient.get<PaginatedFriendRequestsResponse>('/friends/requests', {
      params: { direction },
    })
    return data
  },

  acceptRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(`/friends/requests/${requestId}/accept`)
    return data
  },

  rejectRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(`/friends/requests/${requestId}/reject`)
    return data
  },

  cancelRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(`/friends/requests/${requestId}/cancel`)
    return data
  },

  deleteFriend: async (friendId: number): Promise<void> => {
    await apiClient.delete(`/friends/${friendId}`)
  },
}
