/** 封装房间创建、查询、资料变更、删除及在线浏览人数查询。 */
import { apiClient } from './client'
import type {
  CreateRoomRequest,
  Room,
  RoomWithMessages,
  UpdateRoomRequest,
} from '../types/chat'
import type { Usercnt } from '../types/user'

/** 查询房间列表时的偏移量和数量上限。 */
export interface ListRoomsParams {
  /** 跳过的记录数量。 */
  skip?: number
  /** 本次最多查询的记录数量。 */
  limit?: number
}

/** 房间查询和管理接口。 */
export const roomApi = {
  /**
   * 创建房间。
   * @param data - 房间名称与可选配置。
   * @returns 服务端创建的房间。
   */
  create: async (data: CreateRoomRequest): Promise<Room> => {
    const { data: room } = await apiClient.post<Room>('/rooms/', data)
    return room
  },
  /**
   * 按偏移量查询房间列表。
   * @param params - 跳过数量和返回数量上限。
   * @returns 房间数组。
   */
  list: async (params: ListRoomsParams = {}): Promise<Room[]> => {
    const { data } = await apiClient.get<Room[]>('/rooms/', { params })
    return data
  },

  /**
   * 查询当前用户创建的房间。
   * @returns 自己的房间数组。
   */
  listMine: async (): Promise<Room[]> => {
    const { data } = await apiClient.get<Room[]>('/rooms/mine')
    return data
  },

  /**
   * 查询房间浏览页的在线人数。
   * @returns 在线浏览人数。
   */
  getViewerCount: async (): Promise<Usercnt> => {
    const { data } = await apiClient.get<Usercnt>('/rooms/viewers/count')
    return data
  },
  /**
   * 按经过 URL 编码的名称查询房间。
   * @param name - 房间完整名称。
   * @returns 房间资料。
   */
  getByName: async (name: string): Promise<Room> => {
    const { data } = await apiClient.get<Room>(
      `/rooms/name/${encodeURIComponent(name)}`,
    )
    return data
  },
  /**
   * 按编号查询附带消息的房间详情。
   * @param roomId - 房间编号。
   * @returns 房间详情。
   */
  getById: async (roomId: number): Promise<RoomWithMessages> => {
    const { data } = await apiClient.get<RoomWithMessages>(`/rooms/${roomId}`)
    return data
  },

  /**
   * 提交房间文本资料变更。
   * @param roomId - 房间编号。
   * @param data - 需要完整提供的名称、简介、公告与规则。
   * @returns 服务端返回的已更新字段。
   */
  update: async (
    roomId: number,
    data: Required<UpdateRoomRequest>,
  ): Promise<UpdateRoomRequest> => {
    const { data: updatedFields } = await apiClient.patch<UpdateRoomRequest>(
      `/rooms/${roomId}`,
      data,
    )
    return updatedFields
  },
  /**
   * 删除指定房间。
   * @param roomId - 房间编号。
   * @returns 删除请求完成后结束的 Promise。
   */
  delete: async (roomId: number): Promise<void> => {
    await apiClient.delete(`/rooms/${roomId}`)
  },
}
