/** 资料表单转换、展示统计与账号确认文案。 */
import type { Room } from '../../types/chat.js'
import type { User } from '../../types/user.js'

/** 资料编辑表单中使用的本地字段。 */
export type ProfileForm = {
  /** 待保存的昵称。 */
  nickname: string
  /** 待保存的个人简介。 */
  bio: string
  /** 头像资源目录中的选择键。 */
  avatarKey: string
}

/** 需要用户确认的账号操作；null 表示没有待确认操作。 */
export type ConfirmAction = 'logout' | 'delete' | null

/** 资料页中一项统计的标签和值。 */
export type ProfileStat = {
  /** 统计项展示标签。 */
  label: string
  /** 数值或占位文字。 */
  value: number | string
}

/** 账号确认框的展示文案与样式。 */
export type ConfirmDialogModel = {
  /** 确认框标题。 */
  title: string
  /** 操作影响说明。 */
  description: string
  /** 确认按钮文字。 */
  confirmText: string
  /** 是否使用危险操作样式。 */
  danger: boolean
}

/** 资料统计需要的房间峰值人数字段。 */
type StatsRoom =
  | Pick<Room, 'peak_online_members'>
  | { /** 房间峰值人数，缺省时按零参与统计。 */ peak_online_members?: number }

/**
 * 将用户资料转换为编辑表单，昵称为空时使用用户名。
 * @param user - 当前用户；为空时生成空表单。
 * @returns 可直接绑定资料编辑控件的表单值。
 */
export function toProfileForm(user: User | null | undefined): ProfileForm {
  return {
    nickname: user?.nickname || user?.username || '',
    bio: user?.bio || '',
    avatarKey: user?.avatar_key ?? '',
  }
}

/**
 * 将日期格式化为中文年月日，未提供日期时返回占位符。
 * @param value - 可由 Date 解析的日期字符串。
 * @returns 中文日期或缺省占位符。
 */
export function formatProfileDate(value?: string): string {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

/**
 * 汇总自建房间数量、房间峰值人数之和及加入天数。
 * @param ownedRooms - 用于统计的自建房间。
 * @param createdAt - 账号创建时间；缺省时加入天数显示占位符。
 * @param now - 计算加入天数的当前毫秒时间戳。
 * @returns 资料页使用的标签和值；“评论”标签当前取房间峰值人数之和。
 */
export function buildProfileStats(
  ownedRooms: StatsRoom[],
  createdAt?: string,
  now = Date.now(),
): ProfileStat[] {
  const totalPeak = ownedRooms.reduce(
    (sum, room) => sum + (room.peak_online_members ?? 0),
    0,
  )
  const joinedDays = createdAt
    ? Math.max(
        0,
        Math.floor((now - new Date(createdAt).getTime()) / 86_400_000),
      )
    : null

  return [
    { label: '发布', value: ownedRooms.length },
    { label: '评论', value: totalPeak },
    { label: '加入天数', value: joinedDays ?? '-' },
  ]
}

/**
 * 根据账号操作生成确认文案和危险操作样式标记。
 * @param confirmAction - 待确认操作，null 表示不显示确认框。
 * @param deletingAccount - 是否正在注销，用于切换确认按钮文案。
 * @returns 确认框模型；没有待确认操作时返回 null。
 */
export function buildConfirmDialog(
  confirmAction: ConfirmAction,
  deletingAccount: boolean,
): ConfirmDialogModel | null {
  if (confirmAction === 'logout') {
    return {
      title: '退出登录',
      description:
        '确定要退出当前账号吗？退出后需要重新登录才能继续使用聊天室。',
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
