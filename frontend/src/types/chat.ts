// 通用类型
export interface Usercnt {
  total:number;
}

export type AvatarKey = 'admin' | 'gray' | 'kanra' | 'pink' | 'setton' | 'tanaka' | 'zaika' | 'zawa';

export interface User {
  id: number;
  username: string;
  nickname?: string | null;
  bio?: string | null;
  avatar_key?: AvatarKey | string | null;
  created_at?: string;
}

export interface RoomOwner {
  id: number;
  username: string;
  nickname?: string | null;
  avatar_key?: AvatarKey | string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Room {
  id: number;
  name: string;
  description: string;
  tags: string[];
  min_age: number | null;
  max_age: number | null;
  max_members: number;
  online_members?: number;
  peak_online_members: number;
  owner_id?: number | null;
  owner?: RoomOwner | null;
  notice: string;
  rules: string;
  created_at: string;
}

export interface RoomWithMessages extends Room{
  messages: Message[];
}

export interface Message {
  id: number;
  content: string;
  user_id: number | null;
  room_id: number;
  sender_id?: number;
  recipient_id?: number;
  message_type?: 'user' | 'system';
  client_message_id?: string | null;
  author?: User | null;
  delivery_status?: 'sending' | 'sent' | 'failed';
  created_at: string;
}

export interface PaginatedMessagesResponse {
  items: Message[];
  has_more: boolean;
  next_before_id: number | null;
}

export interface RoomMember {
  id: number;
  username: string;
  nickname?: string | null;
  avatar_key?: AvatarKey | string;
}

export interface RoomMembersEvent {
  room_id: number;
  members: RoomMember[];
}

export interface RoomDeletedEvent {
  room_id: number;
}

export interface CreateRoomRequest {
  name: string;
  description?: string;
  notice?: string;
  rules?: string;
  tags?: string[];
  min_age?: number | null;
  max_age?: number | null;
  max_members?: number;
}

export interface UpdateRoomRequest {
  name?: string;
  description?: string;
  notice?: string;
  rules?: string;
}

export interface LoginCredentials{
  username: string;
  password: string;
}

export interface UserUpdate {
  nickname: string;
  bio: string;
  avatar_key?: AvatarKey | string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface CreateMessageRequest {
  content: string;
  room_id: number;
  client_message_id?: string | null;
}

export type FriendRequestStatus = 'pending' | 'accepted' | 'rejected' | 'canceled';
export type FriendRequestDirection = 'incoming' | 'outgoing' | 'all';

export interface Friend {
  user: User;
  created_at: string;
}

export interface PaginatedFriendsResponse {
  items: Friend[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface FriendRequest {
  id: number;
  requester: User;
  recipient: User;
  status: FriendRequestStatus;
  created_at: string;
  updated_at: string;
}

export interface PaginatedFriendRequestsResponse {
  items: FriendRequest[];
}

export interface CreateFriendRequest {
  recipient_id: number;
}

export interface PrivateMessage extends Message {
  sender_id: number;
  recipient_id: number;
}

export interface PaginatedPrivateMessagesResponse {
  items: PrivateMessage[];
  has_more: boolean;
  next_before_id: number | null;
}



// AI 聊天相关类型
export type AICharacter = 'sakura' | 'rin' | 'mio' | 'yang';

export interface AIChatRequest {
  message: string;  // 1-500字符
  character?: AICharacter;  // 可选：sakura/rin/mio/yang，默认 sakura
}

export interface AIChatResponse {
  content: string;
}
