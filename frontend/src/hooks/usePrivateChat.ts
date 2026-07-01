import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { usersApi } from '@/api/users'
import { privateMessagesApi } from '@/api/privateMessages'
import { socketManager } from '@/services/socket'
import type { Message, PrivateMessage, User } from '@/types/chat'
import { createOptimisticMessage, mergeMessages } from './chatMessageMerge'
import { logger } from '@/utils/logger'

type PrivateChatState = {
  friend: User | null
  messages: Message[]
  initialLoading: boolean
  loadingOlder: boolean
  reconnecting: boolean
  hasMore: boolean
  nextBeforeId: number | null
  error: string | null
}

type PrivateChatAction =
  | { type: 'LOAD_START' }
  | { type: 'LOAD_SUCCESS'; friend: User; messages: Message[]; hasMore: boolean; nextBeforeId: number | null }
  | { type: 'LOAD_FAILURE'; error: string }
  | { type: 'OLDER_START' }
  | { type: 'OLDER_SUCCESS'; messages: Message[]; hasMore: boolean; nextBeforeId: number | null }
  | { type: 'MESSAGES_MERGED'; messages: Message[]; mode: 'head' | 'tail' }
  | { type: 'OPTIMISTIC_MESSAGE_ADDED'; message: Message }
  | { type: 'MESSAGE_ACK'; message: Message }
  | { type: 'MESSAGE_FAILED'; clientMessageId: string }
  | { type: 'RECONNECTING_CHANGED'; reconnecting: boolean }
  | { type: 'ERROR'; error: string | null }

const initialState: PrivateChatState = {
  friend: null,
  messages: [],
  initialLoading: true,
  loadingOlder: false,
  reconnecting: false,
  hasMore: true,
  nextBeforeId: null,
  error: null,
}

function toMessage(message: PrivateMessage): Message {
  return {
    ...message,
    user_id: message.sender_id,
    room_id: 0,
    message_type: 'user',
  }
}

function reducer(state: PrivateChatState, action: PrivateChatAction): PrivateChatState {
  switch (action.type) {
    case 'LOAD_START':
      return { ...initialState, initialLoading: true }
    case 'LOAD_SUCCESS':
      return {
        ...state,
        friend: action.friend,
        messages: mergeMessages([], action.messages, 'head'),
        initialLoading: false,
        hasMore: action.hasMore,
        nextBeforeId: action.nextBeforeId,
        error: null,
      }
    case 'LOAD_FAILURE':
      return { ...state, initialLoading: false, error: action.error }
    case 'OLDER_START':
      return { ...state, loadingOlder: true }
    case 'OLDER_SUCCESS':
      return {
        ...state,
        loadingOlder: false,
        messages: mergeMessages(state.messages, action.messages, 'tail'),
        hasMore: action.hasMore,
        nextBeforeId: action.nextBeforeId,
      }
    case 'MESSAGES_MERGED':
      return { ...state, messages: mergeMessages(state.messages, action.messages, action.mode) }
    case 'OPTIMISTIC_MESSAGE_ADDED':
      return { ...state, messages: mergeMessages(state.messages, [action.message], 'head') }
    case 'MESSAGE_ACK':
      return { ...state, messages: mergeMessages(state.messages, [{ ...action.message, delivery_status: 'sent' }], 'head') }
    case 'MESSAGE_FAILED':
      return {
        ...state,
        messages: state.messages.map((message) =>
          message.client_message_id === action.clientMessageId ? { ...message, delivery_status: 'failed' } : message,
        ),
      }
    case 'RECONNECTING_CHANGED':
      return { ...state, reconnecting: action.reconnecting }
    case 'ERROR':
      return { ...state, error: action.error }
    default:
      return state
  }
}

function makeClientMessageId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function usePrivateChat(friendId: number, user: User | null, isNearHead: () => boolean, scrollToHead: () => void) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [composerValue, setComposerValue] = useState('')
  const stateRef = useRef(state)
  const ackTimers = useRef(new Map<string, number>())

  useEffect(() => {
    stateRef.current = state
  }, [state])

  const clearAckTimer = useCallback((clientMessageId?: string | null) => {
    if (!clientMessageId) return
    const timer = ackTimers.current.get(clientMessageId)
    if (timer) window.clearTimeout(timer)
    ackTimers.current.delete(clientMessageId)
  }, [])

  const loadOlderMessages = useCallback(async () => {
    const current = stateRef.current
    if (!friendId || current.loadingOlder || !current.hasMore) return
    dispatch({ type: 'OLDER_START' })
    const page = await privateMessagesApi.getPageByFriend(friendId, {
      limit: 20,
      beforeId: current.nextBeforeId,
    })
    dispatch({
      type: 'OLDER_SUCCESS',
      messages: page.items.map(toMessage),
      hasMore: page.has_more,
      nextBeforeId: page.next_before_id,
    })
  }, [friendId])

  useEffect(() => {
    if (!friendId) return
    let cancelled = false
    async function loadInitial() {
      dispatch({ type: 'LOAD_START' })
      try {
        const [friend, page] = await Promise.all([
          usersApi.getById(friendId),
          privateMessagesApi.getPageByFriend(friendId, { limit: 20 }),
        ])
        if (cancelled) return
        dispatch({
          type: 'LOAD_SUCCESS',
          friend,
          messages: page.items.map(toMessage),
          hasMore: page.has_more,
          nextBeforeId: page.next_before_id,
        })
      } catch (error) {
        logger.error('[private-chat] initial load failed', {
          message: error instanceof Error ? error.message : String(error),
        })
        if (!cancelled) dispatch({ type: 'LOAD_FAILURE', error: '加载私聊失败' })
      }
    }
    loadInitial()
    return () => {
      cancelled = true
    }
  }, [friendId])

  useEffect(() => {
    if (!friendId || !user) return

    const handlePrevious = (messages: PrivateMessage[]) => {
      dispatch({ type: 'MESSAGES_MERGED', messages: messages.map(toMessage), mode: 'head' })
    }
    const handleAck = (message: PrivateMessage) => {
      clearAckTimer(message.client_message_id)
      dispatch({ type: 'MESSAGE_ACK', message: toMessage(message) })
    }
    const handleNew = (message: PrivateMessage) => {
      const nearHead = isNearHead()
      dispatch({ type: 'MESSAGES_MERGED', messages: [toMessage(message)], mode: 'head' })
      if (nearHead || message.sender_id === user.id) scrollToHead()
    }
    const handleError = (data: { message: string }) => dispatch({ type: 'ERROR', error: data.message })
    const handleReconnect = () => {
      dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: false })
      socketManager.joinPrivateChat(friendId)
    }
    const handleDisconnect = () => dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: true })

    socketManager.joinPrivateChat(friendId)
    socketManager.onPrivatePreviousMessages(handlePrevious)
    socketManager.onPrivateMessageAck(handleAck)
    socketManager.onPrivateNewMessage(handleNew)
    socketManager.onPrivateChatError(handleError)
    socketManager.onReconnect(handleReconnect)
    socketManager.onDisconnect(handleDisconnect)
    const timers = ackTimers.current

    return () => {
      socketManager.offPrivatePreviousMessages(handlePrevious)
      socketManager.offPrivateMessageAck(handleAck)
      socketManager.offPrivateNewMessage(handleNew)
      socketManager.offPrivateChatError(handleError)
      socketManager.offReconnect(handleReconnect)
      socketManager.offDisconnect(handleDisconnect)
      socketManager.leavePrivateChat(friendId)
      timers.forEach((timer) => window.clearTimeout(timer))
      timers.clear()
    }
  }, [clearAckTimer, friendId, isNearHead, scrollToHead, user])

  const sendMessage = useCallback(() => {
    if (!user || !composerValue.trim()) return
    const content = composerValue.trim()
    const clientMessageId = makeClientMessageId()
    dispatch({
      type: 'OPTIMISTIC_MESSAGE_ADDED',
      message: createOptimisticMessage({
        roomId: 0,
        userId: user.id,
        content,
        clientMessageId,
        author: user,
      }),
    })
    setComposerValue('')
    socketManager.sendPrivateMessage(friendId, content, clientMessageId)
    scrollToHead()

    const timer = window.setTimeout(() => {
      dispatch({ type: 'MESSAGE_FAILED', clientMessageId })
      ackTimers.current.delete(clientMessageId)
    }, 10000)
    ackTimers.current.set(clientMessageId, timer)
  }, [composerValue, friendId, scrollToHead, user])

  return {
    ...state,
    composerValue,
    setComposerValue,
    sendMessage,
    loadOlderMessages,
  }
}
