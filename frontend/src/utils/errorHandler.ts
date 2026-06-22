/**
 * 统一错误处理工具
 */
import { logger } from './logger';

interface AxiosError {
  response?: {
    data?: {
      detail?: string;
      message?: string;
    };
    status?: number;
  };
  message?: string;
}

/**
 * 从错误对象中提取用户友好的错误消息
 */
export function extractErrorMessage(error: unknown, defaultMessage = '操作失败'): string {
  if (!error) return defaultMessage;
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && typeof error === 'object') {
    // Axios错误
    if ('response' in error) {
      const axiosError = error as AxiosError;
      if (axiosError.response?.data?.detail) {
        return axiosError.response.data.detail;
      }
      if (axiosError.response?.data?.message) {
        return axiosError.response.data.message;
      }
      if (axiosError.response?.status === 401) {
        return '登录已过期，请重新登录';
      }
      if (axiosError.response?.status === 404) {
        return '请求的资源不存在';
      }
      if (axiosError.response?.status && axiosError.response.status >= 500) {
        return '服务器错误，请稍后重试';
      }
    }
    
    // 普通Error对象
    if ('message' in error && typeof error.message === 'string') {
      return error.message;
    }
  }
  
  return defaultMessage;
}

/**
 * 处理API错误，提取错误消息并可选地显示toast
 */
export function handleApiError(
  error: unknown,
  defaultMessage = '操作失败',
  showToast = true
): string {
  const message = extractErrorMessage(error, defaultMessage);
  
  if (showToast && typeof window !== 'undefined') {
    // 动态导入toast以避免服务端渲染问题
    import('react-hot-toast').then(({ default: toast }) => {
      toast.error(message);
    }).catch(() => {
      logger.error('显示toast失败:', { message });
    });
  }
  
  logger.error('API错误:', { message });
  return message;
}
