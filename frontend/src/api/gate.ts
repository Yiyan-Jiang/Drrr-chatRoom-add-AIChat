/** 封装入口密码验证和基于 Cookie 的入口状态查询。 */
import { apiClient } from './client'
import { AxiosError } from 'axios'
import { logger } from '@/utils/logger'

/** 入口密码与 Cookie 状态查询接口。 */
export const gateApi = {
  /**
   * 以表单请求提交入口密码，并携带 Cookie。
   * @param password - 用户输入的入口密码。
   * @returns 入口验证响应正文。
   */
  verify: async (password: string) => {
    logger.debug('[gate] verify request', { hasPassword: Boolean(password) })
    const params = new URLSearchParams()
    params.append('password', password)
    const { data } = await apiClient.post('/gate/verify', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      withCredentials: true,
    })
    logger.debug('[gate] verify response received')
    return data
  },
  /**
   * 携带 Cookie 查询入口验证状态，失败时记录错误并继续抛出。
   * @returns 入口状态响应正文。
   */
  check: async () => {
    logger.debug('[gate] status request')
    try {
      const { data } = await apiClient.get('/gate/status', {
        withCredentials: true,
      })
      logger.debug('[gate] status response received')
      return data
    } catch (error: unknown) {
      logger.error('[gate] status error', {
        status:
          error instanceof AxiosError ? error.response?.status : undefined,
        message: error instanceof Error ? error.message : String(error),
      })
      if (error instanceof AxiosError) {
        logger.debug('[gate] status error details', {
          status: error.response?.status,
        })
      }
      throw error
    }
  },
}
