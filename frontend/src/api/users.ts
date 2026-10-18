/** 封装用户注册、资料查询、资料更新和删除请求。 */
import { apiClient } from './client'
import type { RegisterRequest } from '../types/auth'
import type { User, Usercnt, UserUpdate } from '../types/user'

/** 用户资料与账号操作接口。 */
export const usersApi = {
  /**
   * 查询已注册用户总数。
   * @returns 用户计数。
   */
  getUserCnt: async (): Promise<Usercnt> => {
    const { data } = await apiClient.get<Usercnt>('/users/count')
    return data
  },
  /**
   * 提交账号凭据完成注册。
   * @param data - 注册用户名和密码。
   * @returns 新建用户资料。
   */
  register: async (data: RegisterRequest): Promise<User> => {
    const { data: user } = await apiClient.post<User>('/users/register', data)
    return user
  },

  /**
   * 查询当前访问令牌对应的用户资料。
   * @returns 当前用户资料。
   */
  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/users/me')
    return data
  },

  /**
   * 更新当前用户资料。
   * @param data - 昵称、简介和可选头像主题。
   * @returns 更新后的用户资料。
   */
  updateMe: async (data: UserUpdate): Promise<User> => {
    const { data: user } = await apiClient.put<User>('/users/me', data)
    return user
  },
  /**
   * 按经过 URL 编码的用户名查询用户。
   * @param username - 登录用户名。
   * @returns 用户资料。
   */
  getByUsername: async (username: string): Promise<User> => {
    const { data } = await apiClient.get<User>(
      `/users/username/${encodeURIComponent(username)}`,
    )
    return data
  },
  /**
   * 按用户编号查询资料。
   * @param userId - 用户编号。
   * @returns 用户资料。
   */
  getById: async (userId: number): Promise<User> => {
    const { data } = await apiClient.get<User>(`/users/${userId}`)
    return data
  },
  /**
   * 更新指定用户资料。
   * @param userId - 用户编号。
   * @param data - 昵称、简介和可选头像主题。
   * @returns 更新后的用户资料。
   */
  update: async (userId: number, data: UserUpdate): Promise<User> => {
    const { data: user } = await apiClient.put<User>(`/users/${userId}`, data)
    return user
  },
  /**
   * 删除指定用户。
   * @param userId - 用户编号。
   * @returns 删除请求完成后结束的 Promise。
   */
  delete: async (userId: number): Promise<void> => {
    await apiClient.delete(`/users/${userId}`)
  },
}
