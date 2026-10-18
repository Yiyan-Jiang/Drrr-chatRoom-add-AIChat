/** 管理私聊历史、Socket.IO 事件、重连回补和乐观发送状态。 */
import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { usersApi } from '@/api/users'
import { privateMessagesApi } from '@/api/privateMessages'
import { socketManager } from '@/services/socket'
import type { Message, PaginatedMessagesResponse } from '@/types/chat'
import type { PrivateMessage } from '@/types/privateMessages'
import type { User } from '@/types/user'
import { createOptimisticMessage, mergeMessages } from './chatMessageMerge'
import { logger } from '@/utils/logger'
import { mergeRecoveredHistory, recoverChatHistory } from './chatHistory'

/** 私聊对象、消息历史和连接加载状态。 */
type PrivateChatState = {
  /** 当前私聊对象资料。 */
  friend: User | null
  /** 当前已载入的消息数组。 */
  messages: Message[]
  /** 首批数据是否仍在加载。 */
  initialLoading: boolean
  /** 是否正在加载更早的历史消息。 */
  loadingOlder: boolean
  /** 连接是否处于等待重连状态。 */
  reconnecting: boolean
  /** 是否还有可继续加载的历史消息。 */
  hasMore: boolean
  /** 加载更早历史时使用的消息编号游标。 */
  nextBeforeId: number | null
  /** 当前操作的错误信息。 */
  error: string | null
}

/** 私聊状态归约器接受的业务事件。 */
type PrivateChatAction =
  | { /** 开始加载私聊对象和首批历史的事件标记。 */ type: 'LOAD_START' }
  | {
      /** 私聊对象和首批历史加载成功的事件标记。 */ type: 'LOAD_SUCCESS'
      /** 首批加载时查询到的私聊对象资料。 */ friend: User
      /** 首批载入的私聊历史消息。 */ messages: Message[]
      /** 本次历史查询后是否仍有更早私聊消息。 */ hasMore: boolean
      /** 继续查询更早私聊消息使用的编号游标。 */ nextBeforeId: number | null
    }
  | {
      /** 私聊首批加载失败的事件标记。 */ type: 'LOAD_FAILURE'
      /** 私聊首批加载失败的提示文本。 */ error: string
    }
  | { /** 开始加载更早私聊历史的事件标记。 */ type: 'OLDER_START' }
  | {
      /** 更早私聊历史加载成功的事件标记。 */ type: 'OLDER_SUCCESS'
      /** 本次查询返回的更早私聊消息。 */ messages: Message[]
      /** 本次历史查询后是否仍有更早私聊消息。 */ hasMore: boolean
      /** 继续查询更早私聊消息使用的编号游标。 */ nextBeforeId: number | null
    }
  | { /** 更早私聊历史加载失败的事件标记。 */ type: 'OLDER_FAILURE' }
  | {
      /** 重连历史回补完成的事件标记。 */ type: 'MESSAGES_RECOVERED'
      /** 重连回补得到的累计历史消息及末页游标。 */ page: PaginatedMessagesResponse
    }
  | {
      /** 合并收到的私聊消息的事件标记。 */ type: 'MESSAGES_MERGED'
      /** 需要与当前私聊历史合并的消息。 */ messages: Message[]
      /** 新记录相对已有消息的拼接方向；合并后仍统一按时间倒序排序。 */ mode:
        'head' | 'tail'
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
      /** 消息等待回执超时的事件标记。 */ type: 'MESSAGE_FAILED'
      /** 需要标记为发送失败的本地消息关联编号。 */ clientMessageId: string
    }
  | {
      /** 连接等待重连状态变化的事件标记。 */ type: 'RECONNECTING_CHANGED'
      /** 连接是否正在等待重连。 */ reconnecting: boolean
    }
  | {
      /** 更新私聊错误提示的事件标记。 */ type: 'ERROR'
      /** 当前私聊错误提示；null 表示清除提示。 */ error: string | null
    }

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

/**
 * 将私聊消息转换为共享展示模型，使用发送方作为作者编号并将房间编号设为 0。
 * @param message - 服务端返回的私聊消息。
 * @returns 用于聊天视口和消息合并的用户消息。
 */
function toMessage(message: PrivateMessage): Message {
  return {
    ...message,
    user_id: message.sender_id,
    room_id: 0,
    message_type: 'user',
  }
}

/**
 * 根据私聊事件更新对象资料、历史分页、消息回执和连接状态。
 * @param state - 当前私聊状态。
 * @param action - 本次需要应用的私聊事件。
 * @returns 应用事件后的状态；未知事件保留原状态。
 */
function reducer(
  state: PrivateChatState,
  action: PrivateChatAction,
): PrivateChatState {
  switch (action.type) {
    case 'LOAD_START':
      return { ...initialState, initialLoading: true }
    case 'LOAD_SUCCESS':
      return {
        ...state,
        friend: action.friend,
        messages: mergeMessages(state.messages, action.messages, 'head'),
        initialLoading: false,
        hasMore: action.hasMore,
        nextBeforeId: action.nextBeforeId,
        error: null,
      }
    case 'LOAD_FAILURE':
      return { ...state, initialLoading: false, error: action.error }
    case 'OLDER_START':
      return { ...state, loadingOlder: true }
    case 'OLDER_FAILURE':
      return { ...state, loadingOlder: false }
    case 'MESSAGES_RECOVERED':
      return { ...state, ...mergeRecoveredHistory(state, action.page) }
    case 'OLDER_SUCCESS':
      return {
        ...state,
        loadingOlder: false,
        messages: mergeMessages(state.messages, action.messages, 'tail'),
        hasMore: action.hasMore,
        nextBeforeId: action.nextBeforeId,
      }
    case 'MESSAGES_MERGED':
      return {
        ...state,
        messages: mergeMessages(state.messages, action.messages, action.mode),
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
    case 'MESSAGE_FAILED':
      return {
        ...state,
        messages: state.messages.map((message) =>
          message.client_message_id === action.clientMessageId
            ? { ...message, delivery_status: 'failed' }
            : message,
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

/**
 * 优先使用 randomUUID 生成私聊关联编号，不可用时组合时间戳和随机十六进制文本。
 * @returns 本地消息与服务端回执使用的关联编号。
 */
function makeClientMessageId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto)
    return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

/**
 * 管理指定好友的私聊会话，合并历史与实时消息并跟踪发送回执。
 * @param friendId - 私聊对象用户编号。
 * @param user - 当前登录用户，未登录时不注册私聊事件。
 * @param isNearHead - 判断视口是否接近最新消息所在顶部。
 * @param scrollToHead - 将视口移动到最新消息的操作。
 * @returns 会话状态、输入框状态、发送和加载更早历史的操作。
 */
export function usePrivateChat(
  friendId: number,
  user: User | null,
  isNearHead: () => boolean,
  scrollToHead: () => void,
) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [composerValue, setComposerValue] = useState('')
  const stateRef = useRef(state)
  const requestScope = useRef({ cancelled: false, friendId })
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

  /** 按当前游标加载更早的私聊消息，忽略已取消会话的结果。 */
  const loadOlderMessages = useCallback(async () => {
    const current = stateRef.current
    const scope = requestScope.current
    if (
      scope.cancelled ||
      scope.friendId !== friendId ||
      !friendId ||
      current.loadingOlder ||
      !current.hasMore
    )
      return
    dispatch({ type: 'OLDER_START' })
    try {
      const page = await privateMessagesApi.getPageByFriend(friendId, {
        limit: 20,
        beforeId: current.nextBeforeId,
      })
      if (scope.cancelled) return
      dispatch({
        type: 'OLDER_SUCCESS',
        messages: page.items.map(toMessage),
        hasMore: page.has_more,
        nextBeforeId: page.next_before_id,
      })
    } catch (error) {
      if (scope.cancelled) return
      logger.error('[private-chat] history fetch failed', {
        message: error instanceof Error ? error.message : String(error),
      })
      dispatch({ type: 'OLDER_FAILURE' })
    }
  }, [friendId])

  useEffect(() => {
    if (!friendId) return
    const scope = { cancelled: false, friendId }
    requestScope.current = scope
    let cancelled = false
    /**
     * 并行查询私聊对象和首批历史，并在当前查询未取消时写入加载结果。
     * @returns 首批加载结束的 Promise；失败时记录日志并写入页面错误状态。
     */
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
        if (!cancelled)
          dispatch({ type: 'LOAD_FAILURE', error: '加载私聊失败' })
      }
    }
    loadInitial()
    return () => {
      cancelled = true
      scope.cancelled = true
    }
  }, [friendId])

  useEffect(() => {
    if (!friendId || !user) return
    let cancelled = false
    let lastMessageId = Math.max(
      0,
      ...stateRef.current.messages.map((message) => message.id),
    )
    let recovering = false
    let recoveryFailed = false
    let recoveryGeneration = 0
    const isCurrentConversation = (message: PrivateMessage) =>
      (message.sender_id === user.id && message.recipient_id === friendId) ||
      (message.sender_id === friendId && message.recipient_id === user.id)

    const handlePrevious = (messages: PrivateMessage[]) => {
      dispatch({
        type: 'MESSAGES_MERGED',
        messages: messages.filter(isCurrentConversation).map(toMessage),
        mode: 'head',
      })
    }
    const handleAck = (message: PrivateMessage) => {
      if (!isCurrentConversation(message)) return
      clearAckTimer(message.client_message_id)
      dispatch({ type: 'MESSAGE_ACK', message: toMessage(message) })
    }
    const handleNew = (message: PrivateMessage) => {
      if (!isCurrentConversation(message)) return
      const nearHead = isNearHead()
      dispatch({
        type: 'MESSAGES_MERGED',
        messages: [toMessage(message)],
        mode: 'head',
      })
      if (nearHead || message.sender_id === user.id) scrollToHead()
    }
    const handleError = (data: {
      /** 私聊事件返回的错误提示文本。 */ message: string
    }) => dispatch({ type: 'ERROR', error: data.message })
    const handleReconnect = () => {
      const generation = ++recoveryGeneration
      recovering = true
      dispatch({ type: 'RECONNECTING_CHANGED', reconnecting: false })
      socketManager.joinPrivateChat(friendId)
      recoverChatHistory(
        (beforeId) =>
          privateMessagesApi.getPageByFriend(friendId, { limit: 50, beforeId }),
        lastMessageId,
        (page) =>
          dispatch({
            type: 'MESSAGES_RECOVERED',
            page: { ...page, items: page.items.map(toMessage) },
          }),
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
          logger.error('[private-chat] reconnect history fetch failed', {
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

    socketManager.joinPrivateChat(friendId)
    socketManager.onPrivatePreviousMessages(handlePrevious)
    socketManager.onPrivateMessageAck(handleAck)
    socketManager.onPrivateNewMessage(handleNew)
    socketManager.onPrivateChatError(handleError)
    socketManager.onReconnect(handleReconnect)
    socketManager.onDisconnect(handleDisconnect)
    const timers = ackTimers.current

    return () => {
      cancelled = true
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

  /** 发送当前私聊草稿并插入本地待发送消息；10 秒未收到回执时标记失败。 */
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
