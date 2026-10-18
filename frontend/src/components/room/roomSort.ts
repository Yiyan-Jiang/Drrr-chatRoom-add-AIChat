/** 房间列表排序规则。 */
import type { Room } from '@/types/chat'

/** 房间列表支持的创建时间、人数和年龄排序选项。 */
export type RoomSortKey =
  | 'created_desc'
  | 'created_asc'
  | 'online_desc'
  | 'max_members_desc'
  | 'min_age_asc'
  | 'max_age_desc'

/** 将房间创建时间转换为排序使用的毫秒时间戳。 */
function createdAtTime(room: Room) {
  return new Date(room.created_at).getTime()
}

/** 比较房间创建时间，使较新的房间排在前面。 */
function compareCreatedDesc(a: Room, b: Room) {
  return createdAtTime(b) - createdAtTime(a)
}

/** 升序比较可空数值，将未设值放到已设值之后。 */
function compareNullableAsc(a: number | null, b: number | null) {
  return (a ?? Number.POSITIVE_INFINITY) - (b ?? Number.POSITIVE_INFINITY)
}

/** 降序比较可空数值，将未设值放到已设值之后。 */
function compareNullableDesc(a: number | null, b: number | null) {
  return (b ?? Number.NEGATIVE_INFINITY) - (a ?? Number.NEGATIVE_INFINITY)
}

/**
 * 复制并排序房间；人数和年龄相同时按创建时间降序排列，未设年龄排在末尾。
 * @param rooms - 待排序的房间，原数组保持不变。
 * @param sortKey - 创建时间、人数或年龄排序方式。
 * @returns 排序后的新数组。
 */
export function sortRooms(rooms: Room[], sortKey: RoomSortKey): Room[] {
  return [...rooms].sort((a, b) => {
    switch (sortKey) {
      case 'created_asc':
        return createdAtTime(a) - createdAtTime(b)
      case 'online_desc':
        return (
          (b.online_members ?? 0) - (a.online_members ?? 0) ||
          compareCreatedDesc(a, b)
        )
      case 'max_members_desc':
        return b.max_members - a.max_members || compareCreatedDesc(a, b)
      case 'min_age_asc':
        return (
          compareNullableAsc(a.min_age, b.min_age) || compareCreatedDesc(a, b)
        )
      case 'max_age_desc':
        return (
          compareNullableDesc(a.max_age, b.max_age) || compareCreatedDesc(a, b)
        )
      case 'created_desc':
      default:
        return compareCreatedDesc(a, b)
    }
  })
}
