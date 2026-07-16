/**
 * 好友类型：服务好友列表、好友申请、申请状态筛选，以及相关页面和 API。
 */
import type { User } from './user'

export type FriendRequestStatus = 'pending' | 'accepted' | 'rejected' | 'canceled'

export type FriendRequestDirection = 'incoming' | 'outgoing' | 'all'

export interface Friend {
  user: User
  created_at: string
}

export interface PaginatedFriendsResponse {
  items: Friend[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface FriendRequest {
  id: number
  requester: User
  recipient: User
  status: FriendRequestStatus
  created_at: string
  updated_at: string
}

export interface PaginatedFriendRequestsResponse {
  items: FriendRequest[]
}

export interface CreateFriendRequest {
  recipient_id: number
}
