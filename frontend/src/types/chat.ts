/**
 * 普通聊天室类型：服务房间列表、房间详情、普通消息、普通聊天室 Socket.IO 事件。
 */
import type { AvatarKey, User } from './user'

export interface RoomOwner {
  id: number
  username: string
  nickname?: string | null
  avatar_key?: AvatarKey | string | null
}

export interface Room {
  id: number
  name: string
  description: string
  tags: string[]
  min_age: number | null
  max_age: number | null
  max_members: number
  online_members?: number
  peak_online_members: number
  owner_id?: number | null
  owner?: RoomOwner | null
  notice: string
  rules: string
  created_at: string
}

export interface RoomWithMessages extends Room {
  messages: Message[]
}

export interface Message {
  id: number
  content: string
  user_id: number | null
  room_id: number
  sender_id?: number
  recipient_id?: number
  message_type?: 'user' | 'system'
  client_message_id?: string | null
  author?: User | null
  delivery_status?: 'sending' | 'sent' | 'failed'
  created_at: string
}

export interface PaginatedMessagesResponse {
  items: Message[]
  has_more: boolean
  next_before_id: number | null
}

export interface RoomMember {
  id: number
  username: string
  nickname?: string | null
  avatar_key?: AvatarKey | string
}

export interface RoomMembersEvent {
  room_id: number
  members: RoomMember[]
}

export interface RoomDeletedEvent {
  room_id: number
}

export interface CreateRoomRequest {
  name: string
  description?: string
  notice?: string
  rules?: string
  tags?: string[]
  min_age?: number | null
  max_age?: number | null
  max_members?: number
}

export interface UpdateRoomRequest {
  name?: string
  description?: string
  notice?: string
  rules?: string
}

export interface CreateMessageRequest {
  content: string
  room_id: number
  client_message_id?: string | null
}
