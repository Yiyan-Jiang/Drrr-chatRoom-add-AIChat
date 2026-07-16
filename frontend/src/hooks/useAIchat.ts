import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import type { AICharacter } from '../types/ai'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const HISTORY_PAGE_SIZE = 30

interface UseAIChatOptions {
  character?: AICharacter
  onError?: (error: Error) => void
}

export interface AIHistoryItem {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  character?: AICharacter | null
  sequence_no: number
  created_at: string
}

interface UseAIChatReturn {
  messages: string
  historyItems: AIHistoryItem[]
  isLoading: boolean
  isHistoryLoading: boolean
  loadingOlderHistory: boolean
  hasMoreHistory: boolean
  error: string | null
  sendMessage: (message: string) => Promise<void>
  clearHistory: () => Promise<void>
  loadOlderHistory: () => Promise<void>
  abort: () => void
}

interface AgentHistoryResponse {
  session_id: string | null
  items: AIHistoryItem[]
  has_more: boolean
  next_before_sequence_no: number | null
}

function createRequestId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `frontend-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function toViewportOrder(items: AIHistoryItem[]): AIHistoryItem[] {
  return [...items].reverse()
}

export function useAIChat(options: UseAIChatOptions = {}): UseAIChatReturn {
  const { character = 'sakura', onError } = options
  const { token, isAuthenticated } = useAuth()

  const [messages, setMessages] = useState('')
  const [historyItems, setHistoryItems] = useState<AIHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isHistoryLoading, setIsHistoryLoading] = useState(false)
  const [loadingOlderHistory, setLoadingOlderHistory] = useState(false)
  const [hasMoreHistory, setHasMoreHistory] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const abortControllerRef = useRef<AbortController | null>(null)
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null)
  const agentSessionIdRef = useRef<string | null>(null)
  const nextBeforeSequenceNoRef = useRef<number | null>(null)
  const loadingOlderRef = useRef(false)
  const messageBufferRef = useRef('')

  const buildHistoryUrl = useCallback((beforeSequenceNo?: number | null) => {
    const params = new URLSearchParams({
      character,
      limit: String(HISTORY_PAGE_SIZE),
    })
    if (beforeSequenceNo != null) {
      params.set('before_sequence_no', String(beforeSequenceNo))
    }
    return `${API_URL}/api/ai/turn/history?${params.toString()}`
  }, [character])

  const applyHistoryPage = useCallback((payload: AgentHistoryResponse, mode: 'replace' | 'append') => {
    agentSessionIdRef.current = payload.session_id
    nextBeforeSequenceNoRef.current = payload.next_before_sequence_no
    setHasMoreHistory(payload.has_more)
    const pageItems = toViewportOrder(payload.items)
    setHistoryItems((prev) => mode === 'replace' ? pageItems : [...prev, ...pageItems])
  }, [])

  const abort = useCallback(() => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
    readerRef.current?.cancel().catch(() => {})
    readerRef.current = null
    messageBufferRef.current = ''
    setMessages('')
    setIsLoading(false)
  }, [])

  useEffect(() => {
    return abort
  }, [abort])

  const loadInitialHistory = useCallback(async () => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
    readerRef.current?.cancel().catch(() => {})
    readerRef.current = null
    agentSessionIdRef.current = null
    nextBeforeSequenceNoRef.current = null
    messageBufferRef.current = ''
    setMessages('')
    setHistoryItems([])
    setHasMoreHistory(false)
    setError(null)
    setIsLoading(false)

    if (!token || !isAuthenticated) return

    setIsHistoryLoading(true)
    try {
      const response = await fetch(buildHistoryUrl(), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('登录已过期，请重新登录')
        }
        throw new Error(`历史记录加载失败 (${response.status})`)
      }
      const payload = (await response.json()) as AgentHistoryResponse
      applyHistoryPage(payload, 'replace')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '历史记录加载失败'
      agentSessionIdRef.current = null
      nextBeforeSequenceNoRef.current = null
      setHistoryItems([])
      setHasMoreHistory(false)
      setError(errorMessage)
      onError?.(err as Error)
    } finally {
      setIsHistoryLoading(false)
    }
  }, [applyHistoryPage, buildHistoryUrl, isAuthenticated, onError, token])

  useEffect(() => {
    void loadInitialHistory()
  }, [loadInitialHistory])

  const loadOlderHistory = useCallback(async () => {
    if (!token || !isAuthenticated || !hasMoreHistory || loadingOlderRef.current) return
    const beforeSequenceNo = nextBeforeSequenceNoRef.current
    if (beforeSequenceNo == null) return

    loadingOlderRef.current = true
    setLoadingOlderHistory(true)
    try {
      const response = await fetch(buildHistoryUrl(beforeSequenceNo), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        throw new Error(`历史记录加载失败 (${response.status})`)
      }
      const payload = (await response.json()) as AgentHistoryResponse
      applyHistoryPage(payload, 'append')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '历史记录加载失败'
      setError(errorMessage)
      onError?.(err as Error)
    } finally {
      loadingOlderRef.current = false
      setLoadingOlderHistory(false)
    }
  }, [applyHistoryPage, buildHistoryUrl, hasMoreHistory, isAuthenticated, onError, token])

  const sendMessage = useCallback(async (message: string) => {
    if (!token || !isAuthenticated) {
      setError('请先登录后再和我聊天')
      return
    }

    abort()
    const controller = new AbortController()
    abortControllerRef.current = controller
    setIsLoading(true)
    setError(null)
    setMessages('')
    messageBufferRef.current = ''

    try {
      const request_id = createRequestId()
      const response = await fetch(`${API_URL}/api/ai/turn/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          request_id,
          session_id: agentSessionIdRef.current,
          message,
          character,
          metadata: { source: 'frontend-ai-chat' },
        }),
        signal: controller.signal,
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('登录已过期，请重新登录')
        }
        if (response.status === 429) {
          throw new Error('请求太频繁了，请稍后再试')
        }
        const payload = await response.json().catch(() => null)
        const detail = payload?.detail?.message ?? payload?.detail?.error_code
        throw new Error(detail || `服务器错误 (${response.status})`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法读取响应流')
      }

      readerRef.current = reader
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      let currentEvent = 'message'

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const events = buffer.split(/\n\n/)
        buffer = events.pop() ?? ''

        for (const rawEvent of events) {
          const lines = rawEvent.split(/\r?\n/)
          const dataLines: string[] = []
          currentEvent = 'message'

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.slice(6).trim()
            } else if (line.startsWith('data:')) {
              dataLines.push(line.slice(5).trimStart())
            }
          }

          const data = dataLines.join('\n')
          if (!data) continue

          if (currentEvent === 'session') {
            agentSessionIdRef.current = data
            continue
          }

          if (currentEvent === 'meta') {
            continue
          }

          if (currentEvent === 'error') {
            const payload = JSON.parse(data) as { error_code?: string; message?: string }
            throw new Error(payload.message || payload.error_code || 'AI 流式响应失败')
          }

          if (data === '[DONE]') {
            setIsLoading(false)
            return
          }

          messageBufferRef.current += data
          setMessages(messageBufferRef.current)
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      if (errorMessage.includes('SESSION_OWNERSHIP_ERROR')) {
        agentSessionIdRef.current = null
      }
      setError(errorMessage)
      onError?.(err as Error)
    } finally {
      abortControllerRef.current = null
      readerRef.current = null
      setIsLoading(false)
    }
  }, [token, isAuthenticated, character, abort, onError])

  const clearHistory = useCallback(async () => {
    if (!token || !isAuthenticated) {
      setError('请先登录才能清空历史记录')
      return
    }

    abort()
    setError(null)
    const response = await fetch(`${API_URL}/api/ai/turn/history?character=${encodeURIComponent(character)}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    if (!response.ok) {
      throw new Error(`清空历史失败 (${response.status})`)
    }

    agentSessionIdRef.current = null
    nextBeforeSequenceNoRef.current = null
    setMessages('')
    setHistoryItems([])
    setHasMoreHistory(false)
  }, [token, isAuthenticated, character, abort])

  return {
    messages,
    historyItems,
    isLoading,
    isHistoryLoading,
    loadingOlderHistory,
    hasMoreHistory,
    error,
    sendMessage,
    clearHistory,
    loadOlderHistory,
    abort,
  }
}
