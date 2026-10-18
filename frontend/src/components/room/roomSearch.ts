/** 房间名称搜索规则。 */
import type { Room } from '@/types/chat'

/**
 * 按去除首尾空白、忽略大小写的名称子串筛选房间。
 * @param rooms - 待筛选的房间。
 * @param query - 房间名称搜索词。
 * @returns 匹配房间；搜索词为空时返回原数组。
 */
export function filterRoomsByName(rooms: Room[], query: string): Room[] {
  const normalizedQuery = query.trim().toLowerCase()

  if (!normalizedQuery) {
    return rooms
  }

  return rooms.filter((room) =>
    room.name.toLowerCase().includes(normalizedQuery),
  )
}
