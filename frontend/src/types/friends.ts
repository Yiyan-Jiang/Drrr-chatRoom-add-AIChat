/** 定义好友关系、好友申请及其查询响应。 */
import type { User } from './user'

/** 好友申请的处理状态。 */
export type FriendRequestStatus =
  'pending' | 'accepted' | 'rejected' | 'canceled'

/** 相对当前用户的好友申请收发方向。 */
export type FriendRequestDirection = 'incoming' | 'outgoing' | 'all'

/** 好友用户及建立关系的时间。 */
export interface Friend {
  /** 对应用户的资料。 */
  user: User
  /** 服务端创建时间字符串。 */
  created_at: string
}

/** 使用页码查询的好友列表响应。 */
export interface PaginatedFriendsResponse {
  /** 当前页记录。 */
  items: Friend[]
  /** 查询范围内的总数量。 */
  total: number
  /** 当前页码。 */
  page: number
  /** 每页记录数量。 */
  page_size: number
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
}

/** 好友申请的参与用户、状态和时间记录。 */
export interface FriendRequest {
  /** 服务端记录编号。 */
  id: number
  /** 申请发起方。 */
  requester: User
  /** 申请接收方。 */
  recipient: User
  /** 好友申请的处理状态。 */
  status: FriendRequestStatus
  /** 服务端创建时间字符串。 */
  created_at: string
  /** 服务端最近更新时间字符串。 */
  updated_at: string
}

/** 好友申请查询返回的记录集合。 */
export interface PaginatedFriendRequestsResponse {
  /** 当前页记录。 */
  items: FriendRequest[]
}

/** 向指定用户发起好友申请的请求。 */
export interface CreateFriendRequest {
  /** 接收方用户编号。 */
  recipient_id: number
}
