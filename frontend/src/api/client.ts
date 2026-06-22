import axios from "axios";
import { logger } from '@/utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers:{
    'Content-Type': 'application/json',
  },
  timeout: 10000,
  withCredentials: true,
})

// 请求拦截器：自动添加Token到请求头
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // 调试gate相关请求
  if (config.url?.includes('/gate')) {
    logger.debug('[gate] request config', {
      url: config.url,
      method: config.method,
      withCredentials: config.withCredentials,
    });
  }
  return config;
});

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  response => {
    // 调试gate相关响应
    if (response.config?.url?.includes('/gate')) {
      logger.debug('[gate] response', {
        url: response.config.url,
        status: response.status,
      });
    }
    return response;
  },
  error => {
    if (error.response) {
      // 服务器响应了错误状态码
      const { status } = error.response;
      
      if (status === 401) {
        // 如果是gate相关接口，不进行跳转（由调用方处理）
        if (error.config?.url && error.config.url.includes('/gate')) {
          return Promise.reject(error);
        }
        // 未授权，清除本地存储
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        // 跳转到登录页，但避免在路由守卫中循环
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login';
        }
      } else if (status === 404) {
        logger.error('资源未找到:', { url: error.config?.url });
      } else if (status >= 500) {
        logger.error('服务器错误:', { status });
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      logger.error('网络错误: 无法连接到服务器');
    } else {
      // 请求配置出错
      logger.error('请求错误:', { message: error.message });
    }
    
    return Promise.reject(error);
  }
);
