/**
 * 认证类型：服务登录、注册、JWT 登录响应，以及 AuthContext 的登录态写入。
 */
import type { User } from './user'

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RegisterRequest {
  username: string
  password: string
}
