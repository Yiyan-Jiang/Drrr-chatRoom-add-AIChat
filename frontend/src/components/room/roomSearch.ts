import type { Room } from '@/types/chat'

export function filterRoomsByName(rooms: Room[], query: string): Room[] {
  const normalizedQuery = query.trim().toLowerCase()

  if (!normalizedQuery) {
    return rooms
  }

  return rooms.filter((room) => room.name.toLowerCase().includes(normalizedQuery))
}
