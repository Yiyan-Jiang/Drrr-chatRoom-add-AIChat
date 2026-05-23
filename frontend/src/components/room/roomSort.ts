import type { Room } from '@/types/chat'

export type RoomSortKey =
  | 'created_desc'
  | 'created_asc'
  | 'online_desc'
  | 'max_members_desc'
  | 'min_age_asc'
  | 'max_age_desc'

function createdAtTime(room: Room) {
  return new Date(room.created_at).getTime()
}

function compareCreatedDesc(a: Room, b: Room) {
  return createdAtTime(b) - createdAtTime(a)
}

function compareNullableAsc(a: number | null, b: number | null) {
  return (a ?? Number.POSITIVE_INFINITY) - (b ?? Number.POSITIVE_INFINITY)
}

function compareNullableDesc(a: number | null, b: number | null) {
  return (b ?? Number.NEGATIVE_INFINITY) - (a ?? Number.NEGATIVE_INFINITY)
}

export function sortRooms(rooms: Room[], sortKey: RoomSortKey): Room[] {
  return [...rooms].sort((a, b) => {
    switch (sortKey) {
      case 'created_asc':
        return createdAtTime(a) - createdAtTime(b)
      case 'online_desc':
        return ((b.online_members ?? 0) - (a.online_members ?? 0)) || compareCreatedDesc(a, b)
      case 'max_members_desc':
        return (b.max_members - a.max_members) || compareCreatedDesc(a, b)
      case 'min_age_asc':
        return compareNullableAsc(a.min_age, b.min_age) || compareCreatedDesc(a, b)
      case 'max_age_desc':
        return compareNullableDesc(a.max_age, b.max_age) || compareCreatedDesc(a, b)
      case 'created_desc':
      default:
        return compareCreatedDesc(a, b)
    }
  })
}
