import type { User } from '@/types/user'

type DisplayUser = Pick<User, 'id' | 'username' | 'nickname'> | null | undefined

export function getUserDisplayName(user: DisplayUser, fallback?: string): string {
  if (user?.nickname?.trim()) return user.nickname.trim()
  if (user?.username?.trim()) return user.username.trim()
  return fallback ?? (user?.id ? `用户${user.id}` : '用户')
}
