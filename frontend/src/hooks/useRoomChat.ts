/** 管理聊天室资料、成员、消息、重连回补及房间操作状态。 */
import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { isAxiosError } from 'axios'
import toast from 'react-hot-toast'
import { roomApi } from '@/api/rooms'
import { messagesApi } from '@/api/messages'
import { socketManager } from '@/services/socket'
import type {
  Message,
  PaginatedMessagesResponse,
  RoomMember,
  RoomWithMessages,
  UpdateRoomRequest,
} from '@/types/chat'
import type { User } from '@/types/user'
import { logger } from '@/utils/logger'
import { createOptimisticMessage, mergeMessages } from './chatMessageMerge'
import { mergeRecoveredHistory, recoverChatHistory } from './chatHistory'

/** 聊天室操作错误的分类和界面提示。 */
type ChatError = {
  /** 供界面区分处理方式的错误类别。 */ kind:
    'not_found' | 'forbidden' | 'network' | 'unknown'
  /** 错误提示文本。 */ message: string
}

/** 聊天室资料、消息历史、成员和交互状态。 */
type RoomChatState = {
  /** 当前房间详情。 */
  room: RoomWithMessages | null
  /** 当前已载入的消息数组。 */
  messages: Message[]
  /** 房间在线成员列表。 */
  members: RoomMember[]
  /** 首批数据是否仍在加载。 */
  initialLoading: boolean
  /** 是否正在加载更早的历史消息。 */
  loadingOlder: boolean
  /** 连接是否处于等待重连状态。 */
  reconnecting: boolean
  /** 是否正在删除房间。 */
  deletingRoom: boolean
  /** 是否正在提交房间资料。 */
  updatingRoom: boolean
  /** 是否正在刷新房间资料。 */
  refreshingRoom: boolean
  /** 是否还有可继续加载的历史消息。 */
  hasMore: boolean
  /** 加载更早历史时使用的消息编号游标。 */
  nextBeforeId: number | null
  /** 当前操作的错误信息。 */
  error: ChatError | null
  /** 视口离开顶部后累计的新消息数量。 */
  unreadNewCount: number
}

/** 聊天室状态归约器接受的业务事件。 */
type RoomChatAction =
  | { /** 开始加载房间详情的事件标记。 */ type: 'ROOM_LOAD_START' }
  | {
      /** 房间详情加载成功的事件标记。 */ type: 'ROOM_LOAD_SUCCESS'
      /** 本次查询返回的房间详情。 */ room: RoomWithMessages
    }
  | {
      /** 房间详情加载失败的事件标记。 */ type: 'ROOM_LOAD_FAILURE'
      /** 本次房间操作的错误分类与提示。 */ error: ChatError
    }
  | {
      /** 聊天室首批消息加载成功的事件标记。 */ type: 'MESSAGES_INITIAL_SUCCESS'
      /** 本次查询返回的聊天室消息分页。 */ page: PaginatedMessagesResponse
    }
  | { /** 开始加载更早房间历史的事件标记。 */ type: 'MESSAGES_OLDER_START' }
  | {
      /** 更早房间历史加载成功的事件标记。 */ type: 'MESSAGES_OLDER_SUCCESS'
      /** 本次查询返回的聊天室消息分页。 */ page: PaginatedMessagesResponse
    }
  | { /** 更早房间历史加载失败的事件标记。 */ type: 'MESSAGES_OLDER_FAILURE' }
  | {
      /** 重连历史回补完成的事件标记。 */ type: 'MESSAGES_RECOVERED'
      /** 重连回补得到的累计历史消息及末页游标。 */ page: PaginatedMessagesResponse
    }
  | {
      /** 添加本地待发送消息的事件标记。 */ type: 'OPTIMISTIC_MESSAGE_ADDED'
      /** 等待服务端回执的本地消息。 */ message: Message
    }
  | {
      /** 收到消息发送回执的事件标记。 */ type: 'MESSAGE_ACK'
      /** 服务端确认保存的消息。 */ message: Message
    }
  | {
      /** 收到聊天室实时消息的事件标记。 */ type: 'NEW_MESSAGE_RECEIVED'
      /** 服务端推送的新消息。 */ message: Message
      /** 收到消息时视口是否接近最新消息所在的顶部。 */ isNearHead: boolean
    }
  | {
      /** 消息等待回执超时的事件标记。 */ type: 'MESSAGE_FAILED'
      /** 需要标记为发送失败的本地消息关联编号。 */ clientMessageId: string
    }
  | {
      /** 收到房间成员快照的事件标记。 */ type: 'MEMBERS_UPDATED'
      /** 房间事件返回的在线成员快照。 */ members: RoomMember[]
    }
  | {
      /** 连接等待重连状态变化的事件标记。 */ type: 'RECONNECTING_CHANGED'
      /** 连接是否正在等待重连。 */ reconnecting: boolean
    }
  | { /** 开始刷新房间详情的事件标记。 */ type: 'ROOM_REFRESH_START' }
  | {
      /** 房间详情刷新成功的事件标记。 */ type: 'ROOM_REFRESH_SUCCESS'
      /** 本次查询返回的房间详情。 */ room: RoomWithMessages
    }
  | {
      /** 房间详情刷新失败的事件标记。 */ type: 'ROOM_REFRESH_FAILURE'
      /** 本次房间操作的错误分类与提示。 */ error: ChatError
    }
  | {
      /** 乐观更新房间资料的事件标记。 */ type: 'ROOM_UPDATE_OPTIMISTIC'
      /** 请求完成前用于界面展示的房间资料副本。 */ room: RoomWithMessages
    }
  | { /** 房间资料更新成功的事件标记。 */ type: 'ROOM_UPDATE_SUCCESS' }
  | {
      /** 房间资料更新失败并回滚的事件标记。 */ type: 'ROOM_UPDATE_ROLLBACK'
      /** 更新失败后需要恢复的房间资料。 */ room: RoomWithMessages
      /** 本次房间操作的错误分类与提示。 */ error: ChatError
    }
  | { /** 开始删除房间的事件标记。 */ type: 'ROOM_DELETE_START' }
  | { /** 房间删除操作完成的事件标记。 */ type: 'ROOM_DELETE_SUCCESS' }
  | {
      /** 房间删除失败的事件标记。 */ type: 'ROOM_DELETE_FAILURE'
      /** 本次房间操作的错误分类与提示。 */ error: ChatError
    }
  | { /** 收到房间删除通知的事件标记。 */ type: 'ROOM_DELETED' }
  | {
      /** 清空新消息未读数量的事件标记。 */ type: 'UNREAD_NEW_MESSAGES_CLEARED'
    }

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

/**
 * 根据房间事件更新资料、成员、历史分页、发送状态和未读数量。
 * @param state - 当前聊天室状态。
 * @param action - 本次需要应用的聊天室事件。
 * @returns 应用事件后的状态；未知事件保留原状态。
 */
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
        messages: mergeMessages(state.messages, action.page.items, 'head'),
        hasMore: action.page.has_more,
        nextBeforeId: action.page.next_before_id,
      }
    case 'MESSAGES_OLDER_START':
      return { ...state, loadingOlder: true }
    case 'MESSAGES_OLDER_FAILURE':
      return { ...state, loadingOlder: false }
    case 'MESSAGES_RECOVERED':
      return { ...state, ...mergeRecoveredHistory(state, action.page) }
    case 'MESSAGES_OLDER_SUCCESS':
      return {
        ...state,
        loadingOlder: false,
        messages: mergeMessages(state.messages, action.page.items, 'tail'),
        hasMore: action.page.has_more,
        nextBeforeId: action.page.next_before_id,
      }
    case 'OPTIMISTIC_MESSAGE_ADDED':
      return {
        ...state,
        messages: mergeMessages(state.messages, [action.message], 'head'),
      }
    case 'MESSAGE_ACK':
      return {
        ...state,
        messages: mergeMessages(
          state.messages,
          [{ ...action.message, delivery_status: 'sent' }],
          'head',
        ),
      }
    case 'NEW_MESSAGE_RECEIVED':
      return {
        ...state,
        messages: mergeMessages(state.messages, [action.message], 'head'),
        unreadNewCount: action.isNearHead
          ? state.unreadNewCount
          : state.unreadNewCount + 1,
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
      return {
        ...state,
        room: action.room,
        updatingRoom: false,
        error: action.error,
      }
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

/**
 * 将无响应、403 和 404 请求错误分类，其余错误使用调用方的提示。
 * @param error - 房间查询或管理操作的错误值。
 * @param fallback - 未匹配已知错误时的界面提示。
 * @returns 包含错误类别与提示文本的对象。
 */
function mapError(error: unknown, fallback: string): ChatError {
  if (isAxiosError(error)) {
    if (!error.response)
      return { kind: 'network', message: '网络连接失败，请稍后再试' }
    if (error.response.status === 403)
      return { kind: 'forbidden', message: '只有房主可以删除房间' }
    if (error.response.status === 404)
      return { kind: 'not_found', message: '房间不存在或已被删除' }
  }
  return { kind: 'unknown', message: fallback }
}

/**
 * 优先使用 randomUUID 生成房间消息关联编号，不可用时组合时间戳和随机十六进制文本。
 * @returns 本地消息与服务端回执使用的关联编号。
 */
function makeClientMessageId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

/**
 * 载入聊天室与历史消息，并管理成员事件、消息回执和房间操作。
 * @param roomId - 当前房间编号。
 * @param user - 当前登录用户，未登录时不注册房间事件。
 * @param isNearHead - 判断视口是否接近最新消息所在顶部。
 * @param scrollToHead - 将视口移动到最新消息的操作。
 * @returns 房间与消息状态、输入框状态及发送、分页和房间管理操作。
 */
export function useRoomChat(
  roomId: number,
  user: User | null,
  isNearHead: () => boolean,
  scrollToHead: () => void,
) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [composerValue, setComposerValue] = useState('')
  const ackTimers = useRef(new Map<string, number>())
  const stateRef = useRef(state)
  const requestScope = useRef({ cancelled: false, roomId })

  useEffect(() => {
    stateRef.current = state
  }, [state])

  const clearAckTimer = useCallback((clientMessageId?: string | null) => {
    if (!clientMessageId) return
    const timer = ackTimers.current.get(clientMessageId)
    if (timer) window.clearTimeout(timer)
    ackTimers.current.delete(clientMessageId)
  }, [])

  /** 按当前历史游标加载更早消息，忽略已取消会话的结果。 */
  const loadOlderMessages = useCallback(async () => {
    const current = stateRef.current
    const scope = requestScope.current
    if (
      scope.cancelled ||
      scope.roomId !== roomId ||
      !roomId ||
      current.loadingOlder ||
      !current.hasMore
    )
      return
    dispatch({ type: 'MESSAGES_OLDER_START' })
    try {
      const page = await messagesApi.getPageByRoom(roomId, {
        limit: 10,
        beforeId: current.nextBeforeId,
      })
      if (scope.cancelled) return
      dispatch({ type: 'MESSAGES_OLDER_SUCCESS', page })
    } catch (error) {
      if (scope.cancelled) return
      logger.error('[chat] history fetch failed', {
        message: error instanceof Error ? error.message : String(error),
      })
      dispatch({ type: 'MESSAGES_OLDER_FAILURE' })
    }
  }, [roomId])

  useEffect(() => {
    if (!roomId || Number.isNaN(roomId)) return
    const scope = { cancelled: false, roomId }
    requestScope.current = scope
    let cancelled = false

    /**
     * 依次查询房间详情和首批消息，并在当前查询未取消时写入结果。
     * @returns 首批加载结束的 Promise；失败时写入分类后的房间错误。
     */
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
        dispatch({
          type: 'ROOM_LOAD_FAILURE',
          error: mapError(error, '获取房间信息失败'),
        })
      }
    }

    loadInitial()
    return () => {
      cancelled = true
      scope.cancelled = true
    }
  }, [roomId])

  useEffect(() => {
    if (!roomId || !user) return
    let cancelled = false
    let lastMessageId = Math.max(
      0,
      ...stateRef.current.messages.map((message) => message.id),
    )
    let recovering = false
    let recoveryFailed = false
    let recoveryGeneration = 0

    const handleAck = (message: Message) => {
      if (message.room_id !== roomId) return
      clearAckTimer(message.client_message_id)
      dispatch({ type: 'MESSAGE_ACK', message })
    }
    const handleNewMessage = (message: Message) => {
      if (message.room_id !== roomId) return
      const nearHead = isNearHead()
      dispatch({ type: 'NEW_MESSAGE_RECEIVED', message, isNearHead: nearHead })
      if (nearHead || message.user_id === user.id) {
        scrollToHead()
      }
    }
    const handleMembers = (data: {
      /** 成员快照所属的房间编号。 */ room_id: number
      /** 成员事件返回的在线成员快照。 */ members: RoomMember[]
    }) => {
      if (data.room_id === roomId)
        dispatch({ type: 'MEMBERS_UPDATED', members: data.members })
    }
    const handleDeleted = (data: {
      /** 被删除的房间编号。 */ room_id: number
    }) => {
      if (data.room_id === roomId) dispatch({ type: 'ROOM_DELETED' })
    }
    const handleReconnect = () => {
      const generation = ++recoveryGeneration
      recovering = true
      dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: false })
      socketManager.joinRoom(roomId)
      recoverChatHistory(
        (beforeId) =>
          messagesApi.getPageByRoom(roomId, { limit: 30, beforeId }),
        lastMessageId,
        (page) => dispatch({ type: 'MESSAGES_RECOVERED', page }),
        () => !cancelled && generation === recoveryGeneration,
      )
        .then(() => {
          if (cancelled || generation !== recoveryGeneration) return
          recovering = false
          recoveryFailed = false
        })
        .catch((error) => {
          if (cancelled || generation !== recoveryGeneration) return
          recovering = false
          recoveryFailed = true
          logger.error('[chat] reconnect history fetch failed', {
            message: error instanceof Error ? error.message : String(error),
          })
        })
    }
    const handleDisconnect = () => {
      if (!recovering && !recoveryFailed) {
        lastMessageId = Math.max(
          0,
          ...stateRef.current.messages.map((message) => message.id),
        )
      }
      recoveryFailed = recoveryFailed || recovering
      recovering = false
      recoveryGeneration++
      dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: true })
    }

    socketManager.joinRoom(roomId)
    socketManager.onMessageAck(handleAck)
    socketManager.onNewMessage(handleNewMessage)
    socketManager.onRoomMembers(handleMembers)
    socketManager.onRoomDeleted(handleDeleted)
    socketManager.onReconnect(handleReconnect)
    socketManager.onDisconnect(handleDisconnect)
    const timers = ackTimers.current

    return () => {
      cancelled = true
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
  }, [clearAckTimer, isNearHead, roomId, scrollToHead, user])

  /** 发送当前草稿并插入本地待发送消息；10 秒未收到回执时标记失败。 */
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

  /**
   * 删除当前房间并返回完成状态；404 按已删除处理，其他失败写入状态并抛出。
   * @returns 删除完成时为 true。
   */
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

  /**
   * 刷新当前房间详情；失败时写入状态并抛出分类错误。
   * @returns 最新房间详情。
   */
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

  /**
   * 乐观更新房间文本资料；失败时恢复旧资料并抛出分类错误。
   * @param data - 名称、简介、公告和规则。
   */
  const updateRoom = useCallback(
    async (data: Required<UpdateRoomRequest>) => {
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
        dispatch({
          type: 'ROOM_UPDATE_ROLLBACK',
          room: previousRoom,
          error: mapped,
        })
        throw mapped
      }
    },
    [roomId],
  )

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
