/** 定义登录凭据、登录响应和注册请求。 */
import type { User } from './user'

/** 登录时提交的用户名和密码。 */
export interface LoginCredentials {
  /** 登录用户名。 */
  username: string
  /** 账号密码。 */
  password: string
}

/** 登录成功后返回的令牌、有效期和用户资料。 */
export interface LoginResponse {
  /** 后续请求使用的访问令牌。 */
  access_token: string
  /** 服务端返回的令牌类型。 */
  token_type: string
  /** 访问令牌有效期，单位为秒。 */
  expires_in: number
  /** 对应用户的资料。 */
  user: User
}

/** 创建用户账号时提交的凭据。 */
export interface RegisterRequest {
  /** 登录用户名。 */
  username: string
  /** 账号密码。 */
  password: string
}
