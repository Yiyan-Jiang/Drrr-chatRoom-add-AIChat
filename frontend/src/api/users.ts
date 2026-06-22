import { apiClient } from "./client";
import type { User, Usercnt } from '../types/chat'

export interface UserUpdate {
  nickname: string;
  bio: string;
  avatar_key?: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export const usersApi = {

  // 获取用户数目
  getUserCnt:async(): Promise<Usercnt> => {
    const { data } = await apiClient.get<Usercnt>('/users/count')
    return data
  },
  
  // 用户注册
  register: async (data: RegisterRequest): Promise<User> => {
    const { data: user } = await apiClient.post<User>('/users/register',data)
    return user
  },

  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/users/me')
    return data
  },

  updateMe: async (data: UserUpdate): Promise<User> => {
    const { data: user } = await apiClient.put<User>('/users/me', data)
    return user
  },

  // 通过用户名查询用户
  getByUsername: async (username: string): Promise<User> => {
    const { data } = await apiClient.get<User>(`/users/username/${encodeURIComponent(username)}`)
    return data
  },

  // 通过 ID 查询用户
  getById: async(userId: number): Promise<User> => {
    const { data } = await apiClient.get<User>(`/users/${userId}`);
    return data
  } ,

  // 更新用户信息
  update: async(userId:number, data: UserUpdate): Promise<User> => {
    const { data: user } = await apiClient.put<User>(`/users/${userId}`,data)
    return user;
  } ,

  // 删除用户
  delete: async (userId: number): Promise<void> => {
    await apiClient.delete(`/users/${userId}`)
  }

}
