/** 维护共享 Socket.IO 连接，并封装房间、私聊和连接事件。 */
import { io, Socket } from 'socket.io-client'
import type { Message, RoomDeletedEvent, RoomMembersEvent } from '@/types/chat'
import type { PrivateMessage } from '@/types/privateMessages'
import { logger } from '@/utils/logger'

const SOCKET_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
/** 房间在线人数的 Socket.IO 事件数据。 */
type RoomMemberCount = {
  /** 关联房间编号。 */ room_id: number
  /** 当前在线成员数。 */ online_members: number
}

// 全局Socket实例
let socketInstance: Socket | null = null
let currentToken: string | null = null

/** 全局 Socket.IO 连接与业务事件接口；无实例时发送和监听操作不执行。 */
export const socketManager = {
  /**
   * 复用同令牌的已连接实例，否则断开旧实例并创建允许重连的新连接。
   * @param token - Socket.IO 认证使用的访问令牌。
   * @returns 当前 Socket.IO 实例；包含 auth 或 token 的连接错误会清理本地会话并跳转登录页。
   */
  connect: (token: string): Socket => {
    // 如果已经有连接且token相同，直接返回
    if (socketInstance?.connected && currentToken === token) {
      return socketInstance
    }

    // 断开现有连接
    if (socketInstance) {
      socketInstance.disconnect()
      socketInstance = null
    }

    currentToken = token

    socketInstance = io(SOCKET_BASE_URL, {
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 10000,
    })

    socketInstance.on('connect', () => {
      logger.debug('Socket连接成功')
    })

    socketInstance.on('disconnect', (reason) => {
      logger.debug('Socket断开连接:', reason)
      if (reason === 'io server disconnect') {
        // 服务器主动断开，可能需要重新认证
        logger.debug('服务器主动断开连接，可能需要重新登录')
      }
    })

    socketInstance.on('connect_error', (error) => {
      logger.error('Socket连接错误:', { message: error.message })
      // 连接错误可能是token无效
      if (error.message.includes('auth') || error.message.includes('token')) {
        logger.error('认证失败，请重新登录')
        // 清除token并跳转到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
      }
    })

    socketInstance.on(
      'error',
      (err: { /** Socket.IO 错误事件的提示文本。 */ message: string }) => {
        logger.error('Socket错误:', { message: err.message })
      },
    )

    return socketInstance
  },

  /**
   * 断开当前连接，并清除共享实例与认证令牌引用。
   * @returns 无返回值。
   */
  disconnect: () => {
    socketInstance?.disconnect()
    socketInstance = null
    currentToken = null
  },
  /**
   * 读取共享实例的已连接状态。
   * @returns 当前实例是否已经连接。
   */
  isConnected: (): boolean => {
    return socketInstance?.connected || false
  },
  /**
   * 读取当前共享连接实例。
   * @returns 当前实例；尚未建立实例时为 null。
   */
  getSocket: (): Socket | null => {
    return socketInstance
  },

  // 客户端 -> 服务端
  /**
   * 发送加入房间请求。
   * @param roomId - 目标房间编号。
   * @returns 无返回值。
   */
  joinRoom: (roomId: number) => {
    socketInstance?.emit('join_room', { room_id: roomId })
  },

  /**
   * 发送离开房间请求。
   * @param roomId - 目标房间编号。
   * @returns 无返回值。
   */
  leaveRoom: (roomId: number) => {
    socketInstance?.emit('leave_room', { room_id: roomId })
  },

  /**
   * 发送聊天室消息；纯空白正文不发送。
   * @param roomId - 目标房间编号。
   * @param content - 待发送正文，发送时保留原文本。
   * @param clientMessageId - 用于关联本地消息与回执的可选编号。
   * @returns 无返回值。
   */
  sendMessage: (roomId: number, content: string, clientMessageId?: string) => {
    if (!content.trim()) return
    socketInstance?.emit('send_message', {
      room_id: roomId,
      content,
      client_message_id: clientMessageId,
    })
  },

  /**
   * 发送加入私聊会话请求。
   * @param friendId - 私聊对象用户编号。
   * @returns 无返回值。
   */
  joinPrivateChat: (friendId: number) => {
    socketInstance?.emit('join_private_chat', { friend_id: friendId })
  },

  /**
   * 发送离开私聊会话请求。
   * @param friendId - 私聊对象用户编号。
   * @returns 无返回值。
   */
  leavePrivateChat: (friendId: number) => {
    socketInstance?.emit('leave_private_chat', { friend_id: friendId })
  },

  /**
   * 向指定用户发送私聊消息；纯空白正文不发送。
   * @param recipientId - 接收方用户编号。
   * @param content - 待发送正文，发送时保留原文本。
   * @param clientMessageId - 用于关联本地消息与回执的可选编号。
   * @returns 无返回值。
   */
  sendPrivateMessage: (
    recipientId: number,
    content: string,
    clientMessageId?: string,
  ) => {
    if (!content.trim()) return
    socketInstance?.emit('send_private_message', {
      recipient_id: recipientId,
      content,
      client_message_id: clientMessageId,
    })
  },

  // 服务端 -> 客户端事件监听
  /**
   * 在当前实例上注册加入房间时返回的历史消息监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onPreviousMessages: (callback: (message: Message[]) => void) => {
    socketInstance?.on('previous_messages', callback)
  },

  /**
   * 从当前实例移除加入房间时返回的历史消息监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offPreviousMessages: (callback: (message: Message[]) => void) => {
    socketInstance?.off('previous_messages', callback)
  },
  /**
   * 在当前实例上注册房间实时新消息监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onNewMessage: (callback: (message: Message) => void) => {
    socketInstance?.on('new_message', callback)
  },

  /**
   * 从当前实例移除房间实时新消息监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offNewMessage: (callback: (message: Message) => void) => {
    socketInstance?.off('new_message', callback)
  },

  /**
   * 在当前实例上注册聊天室消息发送回执监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onMessageAck: (callback: (message: Message) => void) => {
    socketInstance?.on('message_ack', callback)
  },

  /**
   * 从当前实例移除聊天室消息发送回执监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offMessageAck: (callback: (message: Message) => void) => {
    socketInstance?.off('message_ack', callback)
  },

  /**
   * 在当前实例上注册加入私聊时返回的历史消息监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onPrivatePreviousMessages: (
    callback: (messages: PrivateMessage[]) => void,
  ) => {
    socketInstance?.on('private_previous_messages', callback)
  },

  /**
   * 从当前实例移除加入私聊时返回的历史消息监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offPrivatePreviousMessages: (
    callback: (messages: PrivateMessage[]) => void,
  ) => {
    socketInstance?.off('private_previous_messages', callback)
  },

  /**
   * 在当前实例上注册私聊消息发送回执监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onPrivateMessageAck: (callback: (message: PrivateMessage) => void) => {
    socketInstance?.on('private_message_ack', callback)
  },

  /**
   * 从当前实例移除私聊消息发送回执监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offPrivateMessageAck: (callback: (message: PrivateMessage) => void) => {
    socketInstance?.off('private_message_ack', callback)
  },

  /**
   * 在当前实例上注册私聊实时新消息监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onPrivateNewMessage: (callback: (message: PrivateMessage) => void) => {
    socketInstance?.on('private_new_message', callback)
  },

  /**
   * 从当前实例移除私聊实时新消息监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offPrivateNewMessage: (callback: (message: PrivateMessage) => void) => {
    socketInstance?.off('private_new_message', callback)
  },

  /**
   * 在当前实例上注册私聊业务错误监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onPrivateChatError: (
    callback: (data: {
      /** 私聊业务错误的提示文本。 */ message: string
    }) => void,
  ) => {
    socketInstance?.on('private_chat_error', callback)
  },

  /**
   * 从当前实例移除私聊业务错误监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offPrivateChatError: (
    callback: (data: {
      /** 私聊业务错误的提示文本。 */ message: string
    }) => void,
  ) => {
    socketInstance?.off('private_chat_error', callback)
  },

  /**
   * 在当前实例上注册房间删除通知监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onRoomDeleted: (callback: (data: RoomDeletedEvent) => void) => {
    socketInstance?.on('room_deleted', callback)
  },

  /**
   * 从当前实例移除房间删除通知监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offRoomDeleted: (callback: (data: RoomDeletedEvent) => void) => {
    socketInstance?.off('room_deleted', callback)
  },

  /**
   * 在当前实例上注册房间成员快照监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onRoomMembers: (callback: (data: RoomMembersEvent) => void) => {
    socketInstance?.on('room_members', callback)
  },

  /**
   * 从当前实例移除房间成员快照监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offRoomMembers: (callback: (data: RoomMembersEvent) => void) => {
    socketInstance?.off('room_members', callback)
  },

  /**
   * 在当前实例上注册 Socket.IO 管理器重连成功通知监听。
   * @param callback - 连接状态变化时执行的无参数回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onReconnect: (callback: () => void) => {
    socketInstance?.io.on('reconnect', callback)
  },

  /**
   * 从当前实例移除 Socket.IO 管理器重连成功通知监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offReconnect: (callback: () => void) => {
    socketInstance?.io.off('reconnect', callback)
  },

  /**
   * 在当前实例上注册连接断开通知监听。
   * @param callback - 连接状态变化时执行的无参数回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onDisconnect: (callback: () => void) => {
    socketInstance?.on('disconnect', callback)
  },

  /**
   * 从当前实例移除连接断开通知监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offDisconnect: (callback: () => void) => {
    socketInstance?.off('disconnect', callback)
  },
  /**
   * 在当前实例上注册用户加入房间通知监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onUserJoined: (
    callback: (data: {
      /** 加入房间的用户编号。 */ user_id: number
      /** 用户加入的房间编号。 */ room_id: number
    }) => void,
  ) => {
    socketInstance?.on('user_joined', callback)
  },

  /**
   * 从当前实例移除用户加入房间通知监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offUserJoined: (
    callback: (data: {
      /** 加入房间的用户编号。 */ user_id: number
      /** 用户加入的房间编号。 */ room_id: number
    }) => void,
  ) => {
    socketInstance?.off('user_joined', callback)
  },

  /**
   * 在当前实例上注册房间在线人数变更监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onRoomMemberCount: (callback: (data: RoomMemberCount) => void) => {
    socketInstance?.on('room_member_count', callback)
  },

  /**
   * 从当前实例移除房间在线人数变更监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offRoomMemberCount: (callback: (data: RoomMemberCount) => void) => {
    socketInstance?.off('room_member_count', callback)
  },
  /**
   * 在当前实例上注册 Socket.IO 错误通知监听。
   * @param callback - 接收该事件数据的回调；移除监听时需传入同一函数。
   * @returns 无返回值。
   */
  onError: (
    callback: (data: {
      /** Socket.IO 错误事件的提示文本。 */ message: string
    }) => void,
  ) => {
    socketInstance?.on('error', callback)
  },

  /**
   * 从当前实例移除 Socket.IO 错误通知监听。
   * @param callback - 注册监听时传入的同一回调函数。
   * @returns 无返回值。
   */
  offError: (
    callback: (data: {
      /** Socket.IO 错误事件的提示文本。 */ message: string
    }) => void,
  ) => {
    socketInstance?.off('error', callback)
  },
}
