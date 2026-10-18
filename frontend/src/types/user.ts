/** 定义用户资料、头像键、用户计数和资料更新请求。 */
/** 计数接口返回的总数量。 */
export interface Usercnt {
  /** 查询范围内的总数量。 */
  total: number
}

/** 内置头像及气泡主题的资源键。 */
export type AvatarKey =
  'admin' | 'gray' | 'kanra' | 'pink' | 'setton' | 'tanaka' | 'zaika' | 'zawa'

/** 用户资料；可选字段由对应查询接口提供。 */
export interface User {
  /** 服务端记录编号。 */
  id: number
  /** 登录用户名。 */
  username: string
  /** 用户昵称。 */
  nickname?: string | null
  /** 用户简介。 */
  bio?: string | null
  /** 头像主题键。 */
  avatar_key?: AvatarKey | string | null
  /** 服务端创建时间字符串。 */
  created_at?: string
}

/** 更新昵称、简介及可选头像的请求。 */
export interface UserUpdate {
  /** 用户昵称。 */
  nickname: string
  /** 用户简介。 */
  bio: string
  /** 头像主题键。 */
  avatar_key?: AvatarKey | string
}
