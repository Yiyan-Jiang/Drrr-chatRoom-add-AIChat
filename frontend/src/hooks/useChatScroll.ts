import { useCallback, useEffect, useRef } from 'react'

const HEAD_THRESHOLD = 48
const TAIL_THRESHOLD = 96

export function useChatScroll() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const frameRef = useRef<number | null>(null)

  const isNearHead = useCallback(() => {
    const element = containerRef.current
    return !element || element.scrollTop <= HEAD_THRESHOLD
  }, [])

  const scrollToHead = useCallback((behavior: ScrollBehavior = 'smooth') => {
    containerRef.current?.scrollTo({ top: 0, behavior })
  }, [])

  const handleScroll = useCallback((onTailReached: () => void) => {
    if (frameRef.current !== null) return
    frameRef.current = window.requestAnimationFrame(() => {
      frameRef.current = null
      const element = containerRef.current
      if (!element) return
      const distanceToTail = element.scrollHeight - element.clientHeight - element.scrollTop
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
