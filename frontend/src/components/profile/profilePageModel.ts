import type { Room } from '../../types/chat.js'
import type { User } from '../../types/user.js'

export type ProfileForm = {
  nickname: string
  bio: string
  avatarKey: string
}

export type ConfirmAction = 'logout' | 'delete' | null

export type ProfileStat = {
  label: string
  value: number | string
}

export type ConfirmDialogModel = {
  title: string
  description: string
  confirmText: string
  danger: boolean
}

type StatsRoom = Pick<Room, 'peak_online_members'> | { peak_online_members?: number }

export function toProfileForm(user: User | null | undefined): ProfileForm {
  return {
    nickname: user?.nickname || user?.username || '',
    bio: user?.bio || '',
    avatarKey: user?.avatar_key ?? '',
  }
}

export function formatProfileDate(value?: string): string {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

export function buildProfileStats(
  ownedRooms: StatsRoom[],
  createdAt?: string,
  now = Date.now(),
): ProfileStat[] {
  const totalPeak = ownedRooms.reduce((sum, room) => sum + (room.peak_online_members ?? 0), 0)
  const joinedDays = createdAt
    ? Math.max(0, Math.floor((now - new Date(createdAt).getTime()) / 86_400_000))
    : null

  return [
    { label: '发布', value: ownedRooms.length },
    { label: '评论', value: totalPeak },
    { label: '加入天数', value: joinedDays ?? '-' },
  ]
}

export function buildConfirmDialog(
  confirmAction: ConfirmAction,
  deletingAccount: boolean,
): ConfirmDialogModel | null {
  if (confirmAction === 'logout') {
    return {
      title: '退出登录',
      description: '确定要退出当前账号吗？退出后需要重新登录才能继续使用聊天室。',
      confirmText: '退出登录',
      danger: false,
    }
  }

  if (confirmAction === 'delete') {
    return {
      title: '注销账号',
      description: '确定要注销当前账号吗？账号资料会被删除，此操作不可恢复。',
      confirmText: deletingAccount ? '注销中...' : '确认注销',
      danger: true,
    }
  }

  return null
}
