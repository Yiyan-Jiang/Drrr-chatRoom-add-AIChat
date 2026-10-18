/** 封装登录请求，返回供 HTTP 和 Socket.IO 使用的认证信息。 */
import { apiClient } from './client'
import type { LoginCredentials, LoginResponse } from '../types/auth'

/** 登录请求接口。 */
export const authApi = {
  /**
   * 提交用户名和密码进行登录。
   * @param credentials - 登录凭据。
   * @returns 令牌与用户资料。
   */
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const { data } = await apiClient.post<LoginResponse>(
      '/auth/login',
      credentials,
    )
    return data
  },
}
