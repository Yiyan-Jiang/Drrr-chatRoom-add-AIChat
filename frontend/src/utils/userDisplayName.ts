/** 按昵称、用户名和备用文本选择用户显示名称。 */
import type { User } from '@/types/user'

/** 显示名称选择器所需的用户字段，可表示未提供用户。 */
type DisplayUser = Pick<User, 'id' | 'username' | 'nickname'> | null | undefined

/**
 * 优先选择去除首尾空白的昵称或用户名，否则使用备用文本或用户编号。
 * @param user - 待展示的用户资料。
 * @param fallback - 无昵称和用户名时优先使用的文本。
 * @returns 用户显示名称。
 */
export function getUserDisplayName(
  user: DisplayUser,
  fallback?: string,
): string {
  if (user?.nickname?.trim()) return user.nickname.trim()
  if (user?.username?.trim()) return user.username.trim()
  return fallback ?? (user?.id ? `用户${user.id}` : '用户')
}
