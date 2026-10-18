/** 封装好友关系及好友申请的查询和变更请求。 */
import { apiClient } from './client'
import type {
  CreateFriendRequest,
  FriendRequest,
  FriendRequestDirection,
  PaginatedFriendRequestsResponse,
  PaginatedFriendsResponse,
} from '@/types/friends'

/** 好友关系和申请操作接口。 */
export const friendsApi = {
  /**
   * 查询当前用户的好友列表。
   * @param params - 可选页码与每页数量。
   * @returns 好友分页。
   */
  listFriends: async (params?: {
    /** 要查询的好友列表页码。 */ page?: number
    /** 每页最多返回的好友数量。 */ pageSize?: number
  }): Promise<PaginatedFriendsResponse> => {
    const { data } = await apiClient.get<PaginatedFriendsResponse>(
      '/friends/',
      {
        params: { page: params?.page, page_size: params?.pageSize },
      },
    )
    return data
  },

  /**
   * 向指定用户发起好友申请。
   * @param payload - 接收方用户编号。
   * @returns 创建后的好友申请。
   */
  createRequest: async (
    payload: CreateFriendRequest,
  ): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(
      '/friends/requests',
      payload,
    )
    return data
  },

  /**
   * 按收发方向查询好友申请。
   * @param direction - 相对当前用户的收发方向，默认为全部。
   * @returns 好友申请集合。
   */
  listRequests: async (
    direction: FriendRequestDirection = 'all',
  ): Promise<PaginatedFriendRequestsResponse> => {
    const { data } = await apiClient.get<PaginatedFriendRequestsResponse>(
      '/friends/requests',
      {
        params: { direction },
      },
    )
    return data
  },

  /**
   * 接受收到的好友申请。
   * @param requestId - 申请编号。
   * @returns 更新后的好友申请。
   */
  acceptRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(
      `/friends/requests/${requestId}/accept`,
    )
    return data
  },

  /**
   * 拒绝收到的好友申请。
   * @param requestId - 申请编号。
   * @returns 更新后的好友申请。
   */
  rejectRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(
      `/friends/requests/${requestId}/reject`,
    )
    return data
  },

  /**
   * 撤销自己发出的好友申请。
   * @param requestId - 申请编号。
   * @returns 更新后的好友申请。
   */
  cancelRequest: async (requestId: number): Promise<FriendRequest> => {
    const { data } = await apiClient.post<FriendRequest>(
      `/friends/requests/${requestId}/cancel`,
    )
    return data
  },

  /**
   * 删除与指定用户的好友关系。
   * @param friendId - 好友用户编号。
   * @returns 删除请求完成后结束的 Promise。
   */
  deleteFriend: async (friendId: number): Promise<void> => {
    await apiClient.delete(`/friends/${friendId}`)
  },
}
