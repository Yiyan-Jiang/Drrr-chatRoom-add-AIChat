import { apiClient } from "./client";
import type { LoginCredentials, LoginResponse } from "../types/auth";

export const authApi = {
  // 返回 token 用于 socket.io
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const { data } = await apiClient.post<LoginResponse>('/auth/login', credentials);
    return data 
  }
}

