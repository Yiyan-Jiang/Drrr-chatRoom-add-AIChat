/** 定义房间、聊天室消息、历史分页和 Socket.IO 房间事件。 */
import type { AvatarKey, User } from './user'

/** 房间列表和详情中展示的房主摘要。 */
export interface RoomOwner {
  /** 服务端记录编号。 */
  id: number
  /** 登录用户名。 */
  username: string
  /** 用户昵称。 */
  nickname?: string | null
  /** 头像主题键。 */
  avatar_key?: AvatarKey | string | null
}

/** 房间资料、人数配置及在线人数统计。 */
export interface Room {
  /** 服务端记录编号。 */
  id: number
  /** 房间名称。 */
  name: string
  /** 房间简介。 */
  description: string
  /** 房间标签。 */
  tags: string[]
  /** 年龄下限；null 表示未设置。 */
  min_age: number | null
  /** 年龄上限；null 表示未设置。 */
  max_age: number | null
  /** 房间允许的最大成员数。 */
  max_members: number
  /** 当前在线成员数。 */
  online_members?: number
  /** 历史峰值在线成员数。 */
  peak_online_members: number
  /** 房主用户编号。 */
  owner_id?: number | null
  /** 房主摘要资料。 */
  owner?: RoomOwner | null
  /** 房间公告。 */
  notice: string
  /** 房间规则。 */
  rules: string
  /** 服务端创建时间字符串。 */
  created_at: string
}

/** 附带消息数组的房间详情。 */
export interface RoomWithMessages extends Room {
  /** 当前已载入的消息数组。 */
  messages: Message[]
}

/** 共享消息模型，包含服务端字段和本地发送状态。 */
export interface Message {
  /** 服务端记录编号。 */
  id: number
  /** 消息正文。 */
  content: string
  /** 消息作者编号；系统消息可为 null。 */
  user_id: number | null
  /** 关联房间编号。 */
  room_id: number
  /** 发送方用户编号。 */
  sender_id?: number
  /** 接收方用户编号。 */
  recipient_id?: number
  /** 区分用户消息与系统消息。 */
  message_type?: 'user' | 'system'
  /** 关联本地待发送消息与服务端回执的编号。 */
  client_message_id?: string | null
  /** 作者资料；作者不可用时可为空。 */
  author?: User | null
  /** 前端展示的发送中、已发送或失败状态。 */
  delivery_status?: 'sending' | 'sent' | 'failed'
  /** 服务端创建时间字符串。 */
  created_at: string
}

/** 按消息编号向前翻页的聊天室历史。 */
export interface PaginatedMessagesResponse {
  /** 当前页记录。 */
  items: Message[]
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
  /** 下一页查询使用的更早消息编号游标。 */
  next_before_id: number | null
}

/** 房间在线成员的公开资料。 */
export interface RoomMember {
  /** 服务端记录编号。 */
  id: number
  /** 登录用户名。 */
  username: string
  /** 用户昵称。 */
  nickname?: string | null
  /** 头像主题键。 */
  avatar_key?: AvatarKey | string
}

/** 指定房间的在线成员快照事件。 */
export interface RoomMembersEvent {
  /** 关联房间编号。 */
  room_id: number
  /** 房间在线成员列表。 */
  members: RoomMember[]
}

/** 通知指定房间已删除的事件。 */
export interface RoomDeletedEvent {
  /** 关联房间编号。 */
  room_id: number
}

/** 创建房间的表单请求；省略字段由服务端处理。 */
export interface CreateRoomRequest {
  /** 房间名称。 */
  name: string
  /** 房间简介。 */
  description?: string
  /** 房间公告。 */
  notice?: string
  /** 房间规则。 */
  rules?: string
  /** 房间标签。 */
  tags?: string[]
  /** 年龄下限；null 表示未设置。 */
  min_age?: number | null
  /** 年龄上限；null 表示未设置。 */
  max_age?: number | null
  /** 房间允许的最大成员数。 */
  max_members?: number
}

/** 可更新的房间文本资料。 */
export interface UpdateRoomRequest {
  /** 房间名称。 */
  name?: string
  /** 房间简介。 */
  description?: string
  /** 房间公告。 */
  notice?: string
  /** 房间规则。 */
  rules?: string
}

/** 向指定房间提交消息的请求。 */
export interface CreateMessageRequest {
  /** 聊天室消息正文。 */
  content: string
  /** 关联房间编号。 */
  room_id: number
  /** 关联本地待发送消息与服务端回执的编号。 */
  client_message_id?: string | null
}
