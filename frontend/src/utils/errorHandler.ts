/** 提取 API 错误提示，并提供日志与可选的 toast 提示。 */
import { logger } from './logger'

/** 错误提示提取器读取的 HTTP 错误字段子集。 */
interface AxiosError {
  /** HTTP 错误响应及其提示字段。 */
  response?: {
    /** 服务端错误响应的正文。 */
    data?: {
      /** 优先作为用户提示的服务端错误详情。 */
      detail?: string
      /** detail 缺失时读取的服务端错误消息。 */
      message?: string
    }
    /** 用于选择登录过期、资源缺失或服务错误提示的 HTTP 状态码。 */
    status?: number
  }
  /** 错误提示文本。 */
  message?: string
}

/**
 * 按响应正文、HTTP 状态和普通错误消息提取提示。
 * @param error - API 或调用方提供的错误值。
 * @param defaultMessage - 无法提取消息时使用的提示。
 * @returns 可向用户展示的错误文本。
 */
export function extractErrorMessage(
  error: unknown,
  defaultMessage = '操作失败',
): string {
  if (!error) return defaultMessage

  if (typeof error === 'string') {
    return error
  }

  if (error && typeof error === 'object') {
    // Axios错误
    if ('response' in error) {
      const axiosError = error as AxiosError
      if (axiosError.response?.data?.detail) {
        return axiosError.response.data.detail
      }
      if (axiosError.response?.data?.message) {
        return axiosError.response.data.message
      }
      if (axiosError.response?.status === 401) {
        return '登录已过期，请重新登录'
      }
      if (axiosError.response?.status === 404) {
        return '请求的资源不存在'
      }
      if (axiosError.response?.status && axiosError.response.status >= 500) {
        return '服务器错误，请稍后重试'
      }
    }

    // 普通Error对象
    if ('message' in error && typeof error.message === 'string') {
      return error.message
    }
  }

  return defaultMessage
}

/**
 * 记录 API 错误，并按需异步显示 toast 提示。
 * @param error - 请求失败时取得的错误值。
 * @param defaultMessage - 无具体错误信息时使用的提示。
 * @param showToast - 是否在浏览器中显示错误 toast。
 * @returns 已提取并记录的错误文本。
 */
export function handleApiError(
  error: unknown,
  defaultMessage = '操作失败',
  showToast = true,
): string {
  const message = extractErrorMessage(error, defaultMessage)

  if (showToast && typeof window !== 'undefined') {
    // 动态导入toast以避免服务端渲染问题
    import('react-hot-toast')
      .then(({ default: toast }) => {
        toast.error(message)
      })
      .catch(() => {
        logger.error('显示toast失败:', { message })
      })
  }

  logger.error('API错误:', { message })
  return message
}
