import { io, Socket } from 'socket.io-client'
import type { Message, RoomDeletedEvent, RoomMembersEvent } from "../types/chat";

const SOCKET_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
type RoomMemberCount = { room_id: number; online_members: number };

let socketInstance: Socket | null = null;
let currentToken: string | null = null;

export const socketManager = {
  // 初始化连接 Socket.IO
  connect: (token: string): Socket => {
    // 如果已经有连接且token相同，直接返回
    if (socketInstance?.connected && currentToken === token) {
      return socketInstance;
    }

    // 断开现有连接
    if (socketInstance) {
      socketInstance.disconnect();
      socketInstance = null;
    }

    currentToken = token;
    
    socketInstance = io(SOCKET_BASE_URL, {
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 10000,
    });

    socketInstance.on('connect', () => {
      console.log('Socket连接成功');
    });

    socketInstance.on('disconnect', (reason) => {
      console.log('Socket断开连接:', reason);
      if (reason === 'io server disconnect') {
        // 服务器主动断开，可能需要重新认证
        console.log('服务器主动断开连接，可能需要重新登录');
      }
    });

    socketInstance.on('connect_error', (error) => {
      console.error('Socket连接错误:', error.message);
      // 连接错误可能是token无效
      if (error.message.includes('auth') || error.message.includes('token')) {
        console.error('认证失败，请重新登录');
        // 清除token并跳转到登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login';
        }
      }
    });

    socketInstance.on('error', (err: { message: string }) => {
      console.error('Socket错误:', err.message);
    });

    return socketInstance;
  },

  disconnect: () => {
    socketInstance?.disconnect();
    socketInstance = null;
    currentToken = null;
  },

  // 获取当前连接状态
  isConnected: (): boolean => {
    return socketInstance?.connected || false;
  },

  // 获取当前socket实例
  getSocket: (): Socket | null => {
    return socketInstance;
  },

  // 客户端 -> 服务端
  joinRoom: (roomId: number) => {
    socketInstance?.emit('join_room', { room_id: roomId })
  },

  leaveRoom: (roomId: number) => {
    socketInstance?.emit('leave_room', { room_id: roomId })
  },

  sendMessage: (roomId: number, content: string, clientMessageId?: string) => {
    if(!content.trim()) return;
    socketInstance?.emit('send_message', { room_id: roomId, content, client_message_id: clientMessageId })
  },

  // 服务端 -> 客户端事件监听

  
  // 加入返回历史消息
  onPreviousMessages: (callback: (message: Message[]) => void) => {
    socketInstance?.on('previous_messages',callback)
  },

  offPreviousMessages: (callback: (message: Message[]) => void ) => {
    socketInstance?.off('previous_messages',callback)
  },


  // 实时收到新的消息
  onNewMessage: (callback: (message: Message) => void) => {
    socketInstance?.on('new_message',callback)
  },

  offNewMessage: (callback: (message: Message) => void) => {
    socketInstance?.off('new_message',callback)
  },

  onMessageAck: (callback: (message: Message) => void) => {
    socketInstance?.on('message_ack', callback)
  },

  offMessageAck: (callback: (message: Message) => void) => {
    socketInstance?.off('message_ack', callback)
  },

  onRoomDeleted: (callback: (data: RoomDeletedEvent) => void) => {
    socketInstance?.on('room_deleted', callback)
  },

  offRoomDeleted: (callback: (data: RoomDeletedEvent) => void) => {
    socketInstance?.off('room_deleted', callback)
  },

  onRoomMembers: (callback: (data: RoomMembersEvent) => void) => {
    socketInstance?.on('room_members', callback)
  },

  offRoomMembers: (callback: (data: RoomMembersEvent) => void) => {
    socketInstance?.off('room_members', callback)
  },

  onReconnect: (callback: () => void) => {
    socketInstance?.io.on('reconnect', callback)
  },

  offReconnect: (callback: () => void) => {
    socketInstance?.io.off('reconnect', callback)
  },

  onDisconnect: (callback: () => void) => {
    socketInstance?.on('disconnect', callback)
  },

  offDisconnect: (callback: () => void) => {
    socketInstance?.off('disconnect', callback)
  },


  // 有人加入房间通知
  onUserJoined: (callback: (data: { user_id:number; room_id: number }) => void) => {
    socketInstance?.on('user_joined',callback)
  },

  offUserJoined: (callback: (data: { user_id:number; room_id: number }) => void) => {
    socketInstance?.off('user_joined',callback)
  },

  onRoomMemberCount: (callback: (data: RoomMemberCount) => void) => {
    socketInstance?.on('room_member_count', callback)
  },

  offRoomMemberCount: (callback: (data: RoomMemberCount) => void) => {
    socketInstance?.off('room_member_count', callback)
  },


  // 错误返回
  onError: (callback: (data: {message: string}) => void) => {
    socketInstance?.on('error', callback)
  },

  offError: (callback: (data: {message: string}) => void) => {
    socketInstance?.off('error', callback)
  },
}


