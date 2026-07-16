import { apiClient } from "./client";
import type { CreateRoomRequest, Room, RoomWithMessages, UpdateRoomRequest } from "../types/chat";
import type { Usercnt } from "../types/user";



export interface ListRoomsParams {
  skip?: number;
  limit?: number;
}

export const roomApi = {
  // 建房
  create: async (data: CreateRoomRequest): Promise<Room> => {
    const { data: room } = await apiClient.post<Room>('/rooms/',data);
    return room;
  },

  // 拉取房间列表
  list: async (params: ListRoomsParams = {}): Promise<Room[]> => {
    const { data } = await apiClient.get<Room[]>('/rooms/', {params});
    return data
  },

  listMine: async (): Promise<Room[]> => {
    const { data } = await apiClient.get<Room[]>('/rooms/mine')
    return data
  },

  getViewerCount: async (): Promise<Usercnt> => {
    const { data } = await apiClient.get<Usercnt>('/rooms/viewers/count')
    return data
  },

  // 通过名称查询房间
  getByName: async (name: string): Promise<Room> => {
    const { data } = await apiClient.get<Room>(`/rooms/name/${encodeURIComponent(name)}`)
    return data
  },

  // 通过 ID 获取房间详情
  getById: async (roomId: number): Promise<RoomWithMessages> => {
    const { data } = await apiClient.get<RoomWithMessages>(`/rooms/${roomId}`)
    return data
  },

  update: async (roomId: number, data: Required<UpdateRoomRequest>): Promise<UpdateRoomRequest> => {
    const { data: updatedFields } = await apiClient.patch<UpdateRoomRequest>(`/rooms/${roomId}`, data)
    return updatedFields
  },

  // 删除房间
  delete: async (roomId: number): Promise<void> => {
    await apiClient.delete(`/rooms/${roomId}`)
  },

}
