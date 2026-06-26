/**
 * @parm 组件用途：装配我的页面的数据加载、用户操作和资料展示组件。
 */
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { usersApi } from '@/api/users'
import { roomApi } from '@/api/rooms'
import {
  buildConfirmDialog,
  buildProfileStats,
  ConfirmActionDialog,
  OwnedRoomsSection,
  ProfileHeader,
  ProfileStats,
  toProfileForm,
  type ConfirmAction,
  type ProfileForm,
} from '@/components/profile'
import { useAuth } from '@/contexts/AuthContext'
import type { Room } from '@/types/chat'
import { logger } from '@/utils/logger'

export default function MyPage() {
  const { user, updateUser, logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<ProfileForm>(() => toProfileForm(user))
  const [ownedRooms, setOwnedRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deletingAccount, setDeletingAccount] = useState(false)
  const [editing, setEditing] = useState(false)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null)

  useEffect(() => {
    let cancelled = false

    async function loadProfile() {
      try {
        const [currentUser, rooms] = await Promise.all([
          usersApi.getMe(),
          roomApi.listMine(),
        ])
        if (cancelled) return
        updateUser(currentUser)
        setOwnedRooms(rooms)
        setForm(toProfileForm(currentUser))
      } catch (error) {
        logger.error('[profile] failed to load current user', {
          message: error instanceof Error ? error.message : String(error),
        })
        if (!cancelled) toast.error('加载资料失败')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadProfile()
    return () => {
      cancelled = true
    }
  }, [updateUser])

  useEffect(() => {
    if (!pickerOpen) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setPickerOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [pickerOpen])

  useEffect(() => {
    if (!confirmAction) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !deletingAccount) setConfirmAction(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [confirmAction, deletingAccount])

  const normalizedForm = useMemo(
    () => ({
      nickname: form.nickname.trim(),
      bio: form.bio,
      avatarKey: form.avatarKey,
    }),
    [form],
  )
  const hasChanges =
    normalizedForm.nickname !== (user?.nickname || user?.username || '') ||
    normalizedForm.bio !== (user?.bio || '') ||
    normalizedForm.avatarKey !== (user?.avatar_key ?? '')
  const canSave =
    normalizedForm.nickname.length > 0 && normalizedForm.bio.length <= 200 && hasChanges && !saving && !deletingAccount

  const handleSave = async () => {
    if (!normalizedForm.nickname) {
      toast.error('昵称不能为空')
      return
    }
    if (normalizedForm.bio.length > 200) {
      toast.error('简介最多 200 字')
      return
    }

    setSaving(true)
    try {
      const updatedUser = await usersApi.updateMe({
        nickname: normalizedForm.nickname,
        bio: normalizedForm.bio,
        ...(normalizedForm.avatarKey ? { avatar_key: normalizedForm.avatarKey } : {}),
      })
      updateUser(updatedUser)
      setForm(toProfileForm(updatedUser))
      setEditing(false)
      toast.success('资料已保存')
    } catch (error) {
      logger.error('[profile] failed to save current user', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleCancelEdit = () => {
    setForm(toProfileForm(user))
    setPickerOpen(false)
    setEditing(false)
  }

  const handleDeleteAccount = async () => {
    if (!user || deletingAccount) return

    setDeletingAccount(true)
    try {
      await usersApi.delete(user.id)
      toast.success('账号已注销')
      logout()
      navigate('/login', { replace: true })
    } catch (error) {
      logger.error('[profile] failed to delete current user', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('注销账号失败')
    } finally {
      setDeletingAccount(false)
      setConfirmAction(null)
    }
  }

  const handleConfirmAction = async () => {
    if (confirmAction === 'logout') {
      setConfirmAction(null)
      logout()
      navigate('/login', { replace: true })
      return
    }

    if (confirmAction === 'delete') {
      await handleDeleteAccount()
    }
  }

  if (loading && !user) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-zinc-500">
        加载中...
      </div>
    )
  }

  const displayName = user?.nickname || user?.username || '我的页面'
  const stats = buildProfileStats(ownedRooms, user?.created_at)
  const confirmDialog = buildConfirmDialog(confirmAction, deletingAccount)
  const profileRows = [
    ['用户ID', String(user?.id ?? '-')],
    ['注册日', user?.created_at ? new Intl.DateTimeFormat('zh-CN').format(new Date(user.created_at)) : '-'],
    ['最后登录', '在线'],
    ['地区', '未公开'],
    ['一句话', user?.bio?.trim() || '夜晚很安静，想和某个人聊聊天。'],
  ]
  const visitors = [
    { name: 'silent', time: '2小时前' },
    { name: '白夜', time: '5小时前' },
    { name: 'anime_love', time: '昨天' },
    { name: 'void', time: '2天前' },
  ]

  return (
    <div className="dollars-profile-shell h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-7 px-4 py-7 sm:px-8 lg:px-10">
        <section className="dollars-profile-topline flex flex-col gap-7 border-b border-zinc-700/80 pb-7 lg:flex-row lg:items-center lg:justify-between">
          <ProfileHeader
            user={user}
            form={form}
            displayName={displayName}
            editing={editing}
            pickerOpen={pickerOpen}
            saving={saving}
            deletingAccount={deletingAccount}
            canSave={canSave}
            onFormChange={setForm}
            onPickerOpenChange={setPickerOpen}
            onStartEdit={() => setEditing(true)}
            onCancelEdit={handleCancelEdit}
            onSave={handleSave}
            onLogout={() => setConfirmAction('logout')}
            onDeleteAccount={() => setConfirmAction('delete')}
          />
          <ProfileStats stats={stats} />
        </section>

        <section className="dollars-profile-content-grid grid gap-7 lg:grid-cols-[minmax(0,1fr)_390px]">
          <div className="min-w-0">
            <nav
              className="dollars-profile-tabs grid grid-cols-3 border border-zinc-700 text-center text-xs font-semibold text-zinc-300 sm:grid-cols-6"
              aria-label="个人资料菜单"
            >
              {['个人资料', '发布', '评论', '收藏', '喜欢', '设置'].map((item, index) => (
                <button
                  key={item}
                  type="button"
                  className={`h-10 border-zinc-700 transition hover:bg-zinc-900 hover:text-white ${
                    index > 0 ? 'border-l' : ''
                  } ${index === 0 ? 'bg-zinc-950 text-white' : ''}`}
                >
                  {item}
                </button>
              ))}
            </nav>

            <section className="mt-4 rounded-sm border border-zinc-700 bg-black/80 p-5">
              <h2 className="text-sm font-semibold text-white">自我介绍</h2>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-zinc-300">
                {user?.bio?.trim() || '刚开始使用 DOLLARS。\n喜欢在安静的夜晚和大家慢慢聊天。'}
              </p>
            </section>

            <OwnedRoomsSection rooms={ownedRooms} />
          </div>

          <aside className="flex min-w-0 flex-col gap-3">
            <section className="rounded-sm border border-zinc-700 bg-black/80">
              <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold">个人资料</h2>
              <dl className="space-y-3 px-4 py-4 text-xs">
                {profileRows.map(([label, value]) => (
                  <div key={label} className="grid grid-cols-[96px_minmax(0,1fr)] gap-3">
                    <dt className="text-zinc-500">{label}</dt>
                    <dd className="truncate text-right text-zinc-200">{value}</dd>
                  </div>
                ))}
              </dl>
            </section>

            <section className="rounded-sm border border-zinc-700 bg-black/80">
              <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold">徽章</h2>
              <div className="grid grid-cols-4 gap-3 px-4 py-4 text-center text-[11px] text-zinc-400">
                {['第2年', '发布达人', '评论常客', '...'].map((badge) => (
                  <div key={badge} className="flex flex-col items-center gap-2">
                    <span className="grid h-12 w-12 place-items-center rounded-full border border-zinc-500 text-base text-zinc-100">
                      {badge === '...' ? '...' : '◇'}
                    </span>
                    <span className="truncate">{badge}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-sm border border-zinc-700 bg-black/80">
              <h2 className="border-b border-zinc-800 px-4 py-3 text-sm font-semibold">最近访客</h2>
              <ul className="space-y-3 px-4 py-4 text-sm">
                {visitors.map((visitor) => (
                  <li key={visitor.name} className="grid grid-cols-[28px_minmax(0,1fr)_64px] items-center gap-3">
                    <span className="h-6 w-6 rounded-full border border-zinc-600 bg-zinc-900" />
                    <span className="truncate text-zinc-200">{visitor.name}</span>
                    <span className="text-right text-xs text-zinc-500">{visitor.time}</span>
                  </li>
                ))}
              </ul>
            </section>
          </aside>
        </section>

        {confirmDialog && (
          <ConfirmActionDialog
            dialog={confirmDialog}
            deletingAccount={deletingAccount}
            confirmingDelete={confirmAction === 'delete' && deletingAccount}
            onCancel={() => setConfirmAction(null)}
            onConfirm={handleConfirmAction}
          />
        )}
      </div>
    </div>
  )
}
