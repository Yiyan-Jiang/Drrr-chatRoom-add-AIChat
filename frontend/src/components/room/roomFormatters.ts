/** 房间时间和年龄限制的展示格式。 */
import type { Room } from '@/types/chat'

/**
 * 将房间创建时间格式化为中文年月日和时分。
 * @param value - 可由 Date 解析的创建时间。
 * @returns 按浏览器本地时区格式化的时间。
 */
export function formatCreatedAt(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

/**
 * 根据房间年龄上下限生成展示文案，null 表示该侧不限。
 * @param room - 包含年龄上下限的房间。
 * @returns 年龄区间、单侧限制或不限年龄提示。
 */
export function formatAgeRange(room: Room) {
  if (room.min_age === null && room.max_age === null) return '不限年龄'
  if (room.min_age !== null && room.max_age !== null) {
    return `${room.min_age}-${room.max_age} 岁`
  }
  if (room.min_age !== null) return `${room.min_age} 岁以上`
  return `${room.max_age} 岁以下`
}
