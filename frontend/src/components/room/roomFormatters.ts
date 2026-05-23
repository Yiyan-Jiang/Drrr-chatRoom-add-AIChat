import type { Room } from '@/types/chat'

export function formatCreatedAt(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export function formatAgeRange(room: Room) {
  if (room.min_age === null && room.max_age === null) return '不限年龄'
  if (room.min_age !== null && room.max_age !== null) {
    return `${room.min_age}-${room.max_age} 岁`
  }
  if (room.min_age !== null) return `${room.min_age} 岁以上`
  return `${room.max_age} 岁以下`
}
