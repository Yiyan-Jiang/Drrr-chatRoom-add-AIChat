/** 提供聊天视口引用、顶部定位和底部加载触发操作。 */
import { useCallback, useEffect, useRef } from 'react'

const HEAD_THRESHOLD = 48
const TAIL_THRESHOLD = 96

/**
 * 提供聊天视口操作，并用动画帧合并底部检查。
 * @returns 容器引用、顶部邻近判断、滚动到顶部和底部触发函数。
 */
export function useChatScroll() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const frameRef = useRef<number | null>(null)

  /**
   * 判断容器是否位于顶部附近；容器尚未挂载时返回 true。
   * @returns 是否在顶部阈值内。
   */
  const isNearHead = useCallback(() => {
    const element = containerRef.current
    return !element || element.scrollTop <= HEAD_THRESHOLD
  }, [])

  /**
   * 滚动到最新消息所在的容器顶部。
   * @param behavior - 滚动行为，默认为平滑滚动。
   */
  const scrollToHead = useCallback((behavior: ScrollBehavior = 'smooth') => {
    containerRef.current?.scrollTo({ top: 0, behavior })
  }, [])

  /**
   * 在下一动画帧检查底部距离，同一帧只安排一次检查。
   * @param onTailReached - 到达底部阈值时触发的加载历史操作。
   */
  const handleScroll = useCallback((onTailReached: () => void) => {
    if (frameRef.current !== null) return
    frameRef.current = window.requestAnimationFrame(() => {
      frameRef.current = null
      const element = containerRef.current
      if (!element) return
      const distanceToTail =
        element.scrollHeight - element.clientHeight - element.scrollTop
      if (distanceToTail <= TAIL_THRESHOLD) {
        onTailReached()
      }
    })
  }, [])

  useEffect(() => {
    return () => {
      if (frameRef.current !== null) {
        window.cancelAnimationFrame(frameRef.current)
      }
    }
  }, [])

  return {
    containerRef,
    isNearHead,
    scrollToHead,
    handleScroll,
  }
}
