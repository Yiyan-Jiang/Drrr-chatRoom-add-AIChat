import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { isAxiosError } from 'axios'
import toast from 'react-hot-toast'
import { roomApi } from '@/api/rooms'
import { messagesApi } from '@/api/messages'
import { socketManager } from '@/services/socket'
import type { Message, PaginatedMessagesResponse, RoomMember, RoomWithMessages, UpdateRoomRequest } from '@/types/chat'
import type { User } from '@/types/user'
import { logger } from '@/utils/logger'
import { createOptimisticMessage, mergeMessages } from './chatMessageMerge'

type ChatError = { kind: 'not_found' | 'forbidden' | 'network' | 'unknown'; message: string }

type RoomChatState = {
  room: RoomWithMessages | null
  messages: Message[]
  members: RoomMember[]
  initialLoading: boolean
  loadingOlder: boolean
  reconnecting: boolean
  deletingRoom: boolean
  updatingRoom: boolean
  refreshingRoom: boolean
  hasMore: boolean
  nextBeforeId: number | null
  error: ChatError | null
  unreadNewCount: number
}

type RoomChatAction =
  | { type: 'ROOM_LOAD_START' }
  | { type: 'ROOM_LOAD_SUCCESS'; room: RoomWithMessages }
  | { type: 'ROOM_LOAD_FAILURE'; error: ChatError }
  | { type: 'MESSAGES_INITIAL_SUCCESS'; page: PaginatedMessagesResponse }
  | { type: 'MESSAGES_OLDER_START' }
  | { type: 'MESSAGES_OLDER_SUCCESS'; page: PaginatedMessagesResponse }
  | { type: 'OPTIMISTIC_MESSAGE_ADDED'; message: Message }
  | { type: 'MESSAGE_ACK'; message: Message }
  | { type: 'NEW_MESSAGE_RECEIVED'; message: Message; isNearHead: boolean }
  | { type: 'MESSAGE_FAILED'; clientMessageId: string }
  | { type: 'MEMBERS_UPDATED'; members: RoomMember[] }
  | { type: 'RECONNECTING_CHANGED'; reconnecting: boolean }
  | { type: 'ROOM_REFRESH_START' }
  | { type: 'ROOM_REFRESH_SUCCESS'; room: RoomWithMessages }
  | { type: 'ROOM_REFRESH_FAILURE'; error: ChatError }
  | { type: 'ROOM_UPDATE_OPTIMISTIC'; room: RoomWithMessages }
  | { type: 'ROOM_UPDATE_SUCCESS' }
  | { type: 'ROOM_UPDATE_ROLLBACK'; room: RoomWithMessages; error: ChatError }
  | { type: 'ROOM_DELETE_START' }
  | { type: 'ROOM_DELETE_SUCCESS' }
  | { type: 'ROOM_DELETE_FAILURE'; error: ChatError }
  | { type: 'ROOM_DELETED' }
  | { type: 'UNREAD_NEW_MESSAGES_CLEARED' }

const initialState: RoomChatState = {
  room: null,
  messages: [],
  members: [],
  initialLoading: true,
  loadingOlder: false,
  reconnecting: false,
  deletingRoom: false,
  updatingRoom: false,
  refreshingRoom: false,
  hasMore: true,
  nextBeforeId: null,
  error: null,
  unreadNewCount: 0,
}

function reducer(state: RoomChatState, action: RoomChatAction): RoomChatState {
  switch (action.type) {
    case 'ROOM_LOAD_START':
      return { ...initialState, initialLoading: true }
    case 'ROOM_LOAD_SUCCESS':
      return { ...state, room: action.room, initialLoading: false, error: null }
    case 'ROOM_LOAD_FAILURE':
      return { ...state, initialLoading: false, error: action.error }
    case 'MESSAGES_INITIAL_SUCCESS':
      return {
        ...state,
        messages: mergeMessages([], action.page.items, 'head'),
        hasMore: action.page.has_more,
        nextBeforeId: action.page.next_before_id,
      }
    case 'MESSAGES_OLDER_START':
      return { ...state, loadingOlder: true }
    case 'MESSAGES_OLDER_SUCCESS':
      return {
        ...state,
        loadingOlder: false,
        messages: mergeMessages(state.messages, action.page.items, 'tail'),
        hasMore: action.page.has_more,
        nextBeforeId: action.page.next_before_id,
      }
    case 'OPTIMISTIC_MESSAGE_ADDED':
      return { ...state, messages: mergeMessages(state.messages, [action.message], 'head') }
    case 'MESSAGE_ACK':
      return { ...state, messages: mergeMessages(state.messages, [{ ...action.message, delivery_status: 'sent' }], 'head') }
    case 'NEW_MESSAGE_RECEIVED':
      return {
        ...state,
        messages: mergeMessages(state.messages, [action.message], 'head'),
        unreadNewCount: action.isNearHead ? state.unreadNewCount : state.unreadNewCount + 1,
      }
    case 'MESSAGE_FAILED':
      return {
        ...state,
        messages: state.messages.map((message) =>
          message.client_message_id === action.clientMessageId
            ? { ...message, delivery_status: 'failed' }
            : message,
        ),
      }
    case 'MEMBERS_UPDATED':
      return { ...state, members: action.members }
    case 'RECONNECTING_CHANGED':
      return { ...state, reconnecting: action.reconnecting }
    case 'ROOM_REFRESH_START':
      return { ...state, refreshingRoom: true }
    case 'ROOM_REFRESH_SUCCESS':
      return { ...state, room: action.room, refreshingRoom: false, error: null }
    case 'ROOM_REFRESH_FAILURE':
      return { ...state, refreshingRoom: false, error: action.error }
    case 'ROOM_UPDATE_OPTIMISTIC':
      return { ...state, room: action.room, updatingRoom: true, error: null }
    case 'ROOM_UPDATE_SUCCESS':
      return { ...state, updatingRoom: false }
    case 'ROOM_UPDATE_ROLLBACK':
      return { ...state, room: action.room, updatingRoom: false, error: action.error }
    case 'ROOM_DELETE_START':
      return { ...state, deletingRoom: true }
    case 'ROOM_DELETE_SUCCESS':
    case 'ROOM_DELETED':
      return { ...state, deletingRoom: false }
    case 'ROOM_DELETE_FAILURE':
      return { ...state, deletingRoom: false, error: action.error }
    case 'UNREAD_NEW_MESSAGES_CLEARED':
      return { ...state, unreadNewCount: 0 }
    default:
      return state
  }
}

function mapError(error: unknown, fallback: string): ChatError {
  if (isAxiosError(error)) {
    if (!error.response) return { kind: 'network', message: '网络连接失败，请稍后再试' }
    if (error.response.status === 403) return { kind: 'forbidden', message: '只有房主可以删除房间' }
    if (error.response.status === 404) return { kind: 'not_found', message: '房间不存在或已被删除' }
  }
  return { kind: 'unknown', message: fallback }
}

function makeClientMessageId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function useRoomChat(roomId: number, user: User | null, isNearHead: () => boolean, scrollToHead: () => void) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [composerValue, setComposerValue] = useState('')
  const ackTimers = useRef(new Map<string, number>())
  const stateRef = useRef(state)

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
    if (!roomId || current.loadingOlder || !current.hasMore) return
    dispatch({ type: 'MESSAGES_OLDER_START' })
    try {
      const page = await messagesApi.getPageByRoom(roomId, {
        limit: 10,
        beforeId: current.nextBeforeId,
      })
      dispatch({ type: 'MESSAGES_OLDER_SUCCESS', page })
    } catch (error) {
      logger.error('[chat] history fetch failed', {
        message: error instanceof Error ? error.message : String(error),
      })
      dispatch({ type: 'MESSAGES_OLDER_SUCCESS', page: { items: [], has_more: false, next_before_id: null } })
    }
  }, [roomId])

  const reloadLatestMessages = useCallback(async () => {
    const page = await messagesApi.getPageByRoom(roomId, { limit: 10 })
    dispatch({ type: 'MESSAGES_INITIAL_SUCCESS', page })
  }, [roomId])

  useEffect(() => {
    if (!roomId || Number.isNaN(roomId)) return
    let cancelled = false

    async function loadInitial() {
      dispatch({ type: 'ROOM_LOAD_START' })
      try {
        const room = await roomApi.getById(roomId)
        const firstPage = await messagesApi.getPageByRoom(roomId, { limit: 10 })
        if (cancelled) return
        dispatch({ type: 'ROOM_LOAD_SUCCESS', room })
        dispatch({ type: 'MESSAGES_INITIAL_SUCCESS', page: firstPage })
      } catch (error) {
        if (cancelled) return
        dispatch({ type: 'ROOM_LOAD_FAILURE', error: mapError(error, '获取房间信息失败') })
      }
    }

    loadInitial()
    return () => {
      cancelled = true
    }
  }, [roomId])

  useEffect(() => {
    if (!roomId || !user) return

    const handleAck = (message: Message) => {
      clearAckTimer(message.client_message_id)
      dispatch({ type: 'MESSAGE_ACK', message })
    }
    const handleNewMessage = (message: Message) => {
      const nearHead = isNearHead()
      dispatch({ type: 'NEW_MESSAGE_RECEIVED', message, isNearHead: nearHead })
      if (nearHead || message.user_id === user.id) {
        scrollToHead()
      }
    }
    const handleMembers = (data: { room_id: number; members: RoomMember[] }) => {
      if (data.room_id === roomId) dispatch({ type: 'MEMBERS_UPDATED', members: data.members })
    }
    const handleDeleted = (data: { room_id: number }) => {
      if (data.room_id === roomId) dispatch({ type: 'ROOM_DELETED' })
    }
    const handleReconnect = () => {
      dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: false })
      socketManager.joinRoom(roomId)
      reloadLatestMessages().catch((error) =>
        logger.error('[chat] reconnect history fetch failed', {
          message: error instanceof Error ? error.message : String(error),
        }),
      )
    }
    const handleDisconnect = () => dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: true })

    socketManager.joinRoom(roomId)
    socketManager.onMessageAck(handleAck)
    socketManager.onNewMessage(handleNewMessage)
    socketManager.onRoomMembers(handleMembers)
    socketManager.onRoomDeleted(handleDeleted)
    socketManager.onReconnect(handleReconnect)
    socketManager.onDisconnect(handleDisconnect)
    const timers = ackTimers.current

    return () => {
      socketManager.offMessageAck(handleAck)
      socketManager.offNewMessage(handleNewMessage)
      socketManager.offRoomMembers(handleMembers)
      socketManager.offRoomDeleted(handleDeleted)
      socketManager.offReconnect(handleReconnect)
      socketManager.offDisconnect(handleDisconnect)
      socketManager.leaveRoom(roomId)
      timers.forEach((timer) => window.clearTimeout(timer))
      timers.clear()
    }
  }, [clearAckTimer, isNearHead, reloadLatestMessages, roomId, scrollToHead, user])

  const sendMessage = useCallback(() => {
    if (!user || !composerValue.trim()) return
    const content = composerValue.trim()
    const clientMessageId = makeClientMessageId()
    dispatch({
      type: 'OPTIMISTIC_MESSAGE_ADDED',
      message: createOptimisticMessage({
        roomId,
        userId: user.id,
        content,
        clientMessageId,
        author: user,
      }),
    })
    setComposerValue('')
    socketManager.sendMessage(roomId, content, clientMessageId)
    scrollToHead()

    const timer = window.setTimeout(() => {
      dispatch({ type: 'MESSAGE_FAILED', clientMessageId })
      ackTimers.current.delete(clientMessageId)
    }, 10000)
    ackTimers.current.set(clientMessageId, timer)
  }, [composerValue, roomId, scrollToHead, user])

  const deleteRoom = useCallback(async () => {
    dispatch({ type: 'ROOM_DELETE_START' })
    try {
      await roomApi.delete(roomId)
      dispatch({ type: 'ROOM_DELETE_SUCCESS' })
      toast.success('房间已删除')
      return true
    } catch (error) {
      if (isAxiosError(error) && error.response?.status === 404) {
        dispatch({ type: 'ROOM_DELETE_SUCCESS' })
        return true
      }
      const mapped = mapError(error, '删除房间失败')
      dispatch({ type: 'ROOM_DELETE_FAILURE', error: mapped })
      throw mapped
    }
  }, [roomId])

  const refreshRoom = useCallback(async () => {
    dispatch({ type: 'ROOM_REFRESH_START' })
    try {
      const room = await roomApi.getById(roomId)
      dispatch({ type: 'ROOM_REFRESH_SUCCESS', room })
      return room
    } catch (error) {
      const mapped = mapError(error, '刷新房间信息失败')
      dispatch({ type: 'ROOM_REFRESH_FAILURE', error: mapped })
      throw mapped
    }
  }, [roomId])

  const updateRoom = useCallback(async (data: Required<UpdateRoomRequest>) => {
    const currentRoom = stateRef.current.room
    if (!currentRoom) return

    const previousRoom = currentRoom
    dispatch({
      type: 'ROOM_UPDATE_OPTIMISTIC',
      room: {
        ...currentRoom,
        ...data,
      },
    })

    try {
      await roomApi.update(roomId, data)
      dispatch({ type: 'ROOM_UPDATE_SUCCESS' })
    } catch (error) {
      const mapped = mapError(error, '更新房间信息失败')
      dispatch({ type: 'ROOM_UPDATE_ROLLBACK', room: previousRoom, error: mapped })
      throw mapped
    }
  }, [roomId])

  return {
    ...state,
    composerValue,
    setComposerValue,
    sendMessage,
    loadOlderMessages,
    refreshRoom,
    updateRoom,
    deleteRoom,
    clearUnread: () => dispatch({ type: 'UNREAD_NEW_MESSAGES_CLEARED' }),
  }
}
