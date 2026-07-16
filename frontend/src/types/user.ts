/**
 * 用户类型：服务用户资料、头像、用户计数、个人信息更新，以及其他业务里的用户引用。
 */
export interface Usercnt {
  total: number
}

export type AvatarKey = 'admin' | 'gray' | 'kanra' | 'pink' | 'setton' | 'tanaka' | 'zaika' | 'zawa'

export interface User {
  id: number
  username: string
  nickname?: string | null
  bio?: string | null
  avatar_key?: AvatarKey | string | null
  created_at?: string
}

export interface UserUpdate {
  nickname: string
  bio: string
  avatar_key?: AvatarKey | string
}
