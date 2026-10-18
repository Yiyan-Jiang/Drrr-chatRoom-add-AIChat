/** 查询用户总数，并在组件卸载后停止写入查询状态。 */
import { useCallback, useEffect, useRef, useState } from 'react'
import type { Usercnt } from '../types/user'
import { usersApi } from '../api/users'
import { logger } from '../utils/logger'

/**
 * 查询用户总数，将失败原因写入日志并提供界面错误状态。
 * @returns 用户计数、初次加载状态、错误提示和重新查询函数。
 */
export function useUserCount() {
  const [data, setData] = useState<Usercnt | null>(null)
  const [loading, serLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cancelledRef = useRef(false)

  /** 刷新用户总数与错误状态；卸载后不再写入查询结果。 */
  const fetchUserCount = useCallback(async (): Promise<void> => {
    setError(null)

    try {
      const res: Usercnt = await usersApi.getUserCnt()
      if (!cancelledRef.current) {
        setData(res)
      }
    } catch (err) {
      logger.error('获取用户数量失败', {
        message: err instanceof Error ? err.message : String(err),
      })
      if (!cancelledRef.current) {
        setError('获取失败')
      }
    } finally {
      if (!cancelledRef.current) {
        serLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    cancelledRef.current = false
    const timer = window.setTimeout(() => {
      fetchUserCount()
    }, 0)

    return () => {
      window.clearTimeout(timer)
      cancelledRef.current = true
    }
  }, [fetchUserCount])

  return {
    data,
    loading,
    error,
    refetch: fetchUserCount,
  }
}
