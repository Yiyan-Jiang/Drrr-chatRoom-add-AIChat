import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { chatAvatarCatalog, resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { usersApi } from '@/api/users'
import { roomApi } from '@/api/rooms'
import { useAuth } from '@/contexts/AuthContext'
import type { Room } from '@/types/chat'
import { logger } from '@/utils/logger'

type ProfileForm = {
  nickname: string
  bio: string
  avatarKey: string
}

type ConfirmAction = 'logout' | 'delete' | null

function toForm(user: ReturnType<typeof useAuth>['user']): ProfileForm {
  return {
    nickname: user?.nickname || user?.username || '',
    bio: user?.bio || '',
    avatarKey: user?.avatar_key ?? '',
  }
}

function formatDate(value?: string): string {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

export default function MyPage() {
  const { user, updateUser, logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<ProfileForm>(() => toForm(user))
  const [ownedRooms, setOwnedRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deletingAccount, setDeletingAccount] = useState(false)
  const [editing, setEditing] = useState(false)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null)
  const avatarAssets = resolveChatAvatarAssets(form.avatarKey || user?.avatar_key)

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
        setForm(toForm(currentUser))
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
    setForm(toForm(user))
  }, [user])

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
      setForm(toForm(updatedUser))
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
    setForm(toForm(user))
    setPickerOpen(false)
    setEditing(false)
  }

  const handleLogout = () => {
    setConfirmAction('logout')
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

  const profileChecklist = [
    {
      key: 'nickname',
      label: '设置个性昵称',
      done: Boolean(user?.nickname && user.nickname !== user.username),
    },
    {
      key: 'bio',
      label: '填写个人简介',
      done: Boolean(user?.bio && user.bio.trim().length > 0),
    },
    {
      key: 'avatar',
      label: '选择专属头像',
      done: Boolean(user?.avatar_key),
    },
  ]
  const completedCount = profileChecklist.filter((item) => item.done).length
  const completeness = Math.round((completedCount / profileChecklist.length) * 100)
  const profileComplete = completedCount === profileChecklist.length

  const totalPeak = ownedRooms.reduce((sum, room) => sum + (room.peak_online_members ?? 0), 0)
  const joinedDays = user?.created_at
    ? Math.max(0, Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86_400_000))
    : null
  const stats = [
    { label: '创建房间', value: ownedRooms.length },
    { label: '累计峰值', value: totalPeak },
    { label: '加入天数', value: joinedDays ?? '-' },
  ]

  const confirmDialog =
    confirmAction === 'logout'
      ? {
          title: '退出登录',
          description: '确定要退出当前账号吗？退出后需要重新登录才能继续使用聊天室。',
          confirmText: '退出登录',
          danger: false,
        }
      : confirmAction === 'delete'
        ? {
            title: '注销账号',
            description: '确定要注销当前账号吗？账号资料会被删除，此操作不可恢复。',
            confirmText: deletingAccount ? '注销中...' : '确认注销',
            danger: true,
          }
        : null

  return (
    <div className="h-full min-h-0 overflow-auto bg-[#090909] text-zinc-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-12 sm:px-10">
      <section className="flex items-start justify-between gap-5">
        <div className="flex min-w-0 items-start gap-5">
        <div className="relative shrink-0">
          <button
            type="button"
            onClick={() => setPickerOpen((open) => !open)}
            disabled={!editing}
            className="group relative block h-20 w-20 overflow-hidden rounded-2xl border border-zinc-800 transition enabled:hover:border-zinc-500 disabled:cursor-default"
            aria-label="更换头像"
          >
            <img src={avatarAssets.avatar} alt="用户头像" className="h-full w-full object-cover" />
            {editing && (
              <span className="absolute inset-x-0 bottom-0 bg-black/60 py-0.5 text-center text-[10px] font-medium text-zinc-200 opacity-0 transition group-hover:opacity-100">
                更换
              </span>
            )}
          </button>

          {pickerOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setPickerOpen(false)} />
              <div className="absolute left-0 top-[calc(100%+0.5rem)] z-20 w-64 rounded-xl border border-zinc-800 bg-zinc-950 p-3 shadow-xl shadow-black/40">
                <p className="mb-2 px-1 text-[11px] font-medium uppercase tracking-wider text-zinc-500">选择头像</p>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(chatAvatarCatalog).map(([key, assets]) => {
                    const selected = key === form.avatarKey
                    return (
                      <button
                        key={key}
                        type="button"
                        onClick={() => {
                          setForm((current) => ({ ...current, avatarKey: key }))
                          setPickerOpen(false)
                        }}
                        className={`overflow-hidden rounded-lg border transition ${
                          selected
                            ? 'border-zinc-100 ring-1 ring-zinc-100'
                            : 'border-zinc-800 hover:border-zinc-500'
                        }`}
                        aria-label={`头像 ${key}`}
                        aria-pressed={selected}
                      >
                        <img src={assets.avatar} alt={key} className="h-12 w-12 object-cover" />
                      </button>
                    )
                  })}
                </div>
              </div>
            </>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-zinc-600">个人资料</p>
          {editing ? (
            <input
              value={form.nickname}
              maxLength={64}
              autoFocus
              onChange={(event) => setForm((current) => ({ ...current, nickname: event.target.value }))}
              className="mt-1 h-10 w-full max-w-xs rounded-lg border border-zinc-800 bg-black px-3 text-2xl font-semibold text-zinc-100 outline-none transition focus:border-zinc-500"
            />
          ) : (
            <h1 className="mt-1 truncate text-3xl font-semibold tracking-tight">{displayName}</h1>
          )}
          <p className="mt-1.5 font-mono text-sm text-zinc-500">@{user?.username || '-'}</p>

          <div className="mt-3">
            {editing ? (
              <>
                <div className="mb-1.5 flex items-center justify-between text-xs font-medium uppercase tracking-wider text-zinc-500">
                  <span>简介</span>
                  <span className="font-mono tabular-nums text-zinc-600">{form.bio.length}/200</span>
                </div>
                <textarea
                  value={form.bio}
                  maxLength={200}
                  rows={4}
                  onChange={(event) => setForm((current) => ({ ...current, bio: event.target.value }))}
                  className="w-full resize-none rounded-lg border border-zinc-800 bg-black px-3.5 py-2.5 text-sm leading-relaxed text-zinc-100 outline-none transition focus:border-zinc-500"
                />
              </>
            ) : (
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">
                {user?.bio?.trim() ? user.bio : <span className="text-zinc-600">还没有填写简介</span>}
              </p>
            )}
          </div>
        </div>
        </div>

        <div className="flex shrink-0 flex-wrap items-center justify-end gap-3">
          {editing ? (
            <>
              <button
                type="button"
                disabled={!canSave}
                onClick={handleSave}
                className="h-9 rounded-lg bg-zinc-100 px-5 text-sm font-semibold text-black transition active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-600"
              >
                {saving ? '保存中...' : '保存'}
              </button>
              <button
                type="button"
                disabled={saving || deletingAccount}
                onClick={handleCancelEdit}
                className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-600 disabled:cursor-not-allowed disabled:text-zinc-700"
              >
                取消
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setEditing(true)}
              disabled={deletingAccount}
              className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100"
            >
              编辑
            </button>
          )}
          <button
            type="button"
            onClick={handleLogout}
            disabled={saving || deletingAccount}
            className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:text-zinc-700"
          >
            退出登录
          </button>
          <button
            type="button"
            onClick={() => setConfirmAction('delete')}
            disabled={!user || saving || deletingAccount}
            className="h-9 rounded-lg border border-red-900/70 px-5 text-sm text-red-300 transition hover:border-red-500 hover:text-red-100 disabled:cursor-not-allowed disabled:border-zinc-800 disabled:text-zinc-700"
          >
            {deletingAccount ? '注销中...' : '注销账号'}
          </button>
        </div>
      </section>

      <section className="grid grid-cols-3 gap-3">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-2xl border border-zinc-800 bg-zinc-950/40 px-4 py-5 text-center sm:text-left"
          >
            <div className="font-mono text-2xl font-semibold tabular-nums text-zinc-100">{stat.value}</div>
            <div className="mt-1 text-xs text-zinc-500">{stat.label}</div>
          </div>
        ))}
      </section>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-950/40 p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold tracking-tight">资料完整度</h2>
            <p className="mt-0.5 text-xs text-zinc-500">
              {profileComplete ? '资料已完善，很棒。' : '完善资料能让别人更快认识你。'}
            </p>
          </div>
          <span
            className={`font-mono text-2xl font-semibold tabular-nums ${
              profileComplete ? 'text-emerald-400' : 'text-zinc-100'
            }`}
          >
            {completeness}%
          </span>
        </div>

        <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-zinc-800">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              profileComplete ? 'bg-emerald-500/80' : 'bg-zinc-300'
            }`}
            style={{ width: `${completeness}%` }}
          />
        </div>

        {!profileComplete && (
          <ul className="mt-4 flex flex-col gap-2">
            {profileChecklist.map((item) => (
              <li key={item.key} className="flex items-center gap-2.5 text-sm">
                <span
                  className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[10px] ${
                    item.done
                      ? 'border-emerald-500/60 bg-emerald-500/20 text-emerald-400'
                      : 'border-zinc-700 text-transparent'
                  }`}
                >
                  ✓
                </span>
                <span className={item.done ? 'text-zinc-500 line-through' : 'text-zinc-300'}>
                  {item.label}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between">
          <h2 className="text-lg font-semibold tracking-tight">我创建的房间</h2>
          <span className="font-mono text-sm tabular-nums text-zinc-500">{ownedRooms.length} 个</span>
        </div>

        {ownedRooms.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-zinc-800 px-6 py-12 text-center">
            <p className="text-sm font-medium text-zinc-300">还没有创建房间</p>
            <p className="max-w-sm text-xs leading-relaxed text-zinc-500">
              创建一个属于你的聊天室，邀请大家一起聊天、分享与讨论。
            </p>
            <Link
              to="/home/rooms"
              className="mt-1 inline-flex h-9 items-center rounded-lg bg-zinc-100 px-5 text-sm font-semibold text-black transition active:scale-[0.98]"
            >
              去创建房间
            </Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {ownedRooms.map((room) => (
              <Link
                key={room.id}
                to={`/chat/${room.id}`}
                className="group flex flex-col rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 transition hover:border-zinc-600 hover:bg-zinc-900/40"
              >
                <div className="truncate text-sm font-semibold text-zinc-100">{room.name}</div>
                <div className="mt-1 line-clamp-2 text-xs leading-relaxed text-zinc-500">
                  {room.description || '暂无简介'}
                </div>

                {room.tags.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {room.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border border-zinc-800 bg-zinc-900/60 px-2 py-0.5 text-[10px] text-zinc-400"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                <div className="mt-3 flex items-center justify-between font-mono text-xs tabular-nums text-zinc-500">
                  <span className="flex items-center gap-1.5">
                    <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500/70" />
                    {room.online_members ?? 0} / {room.max_members}
                  </span>
                  <span className="text-zinc-600">峰值 {room.peak_online_members}</span>
                </div>
                <div className="mt-1.5 text-[11px] text-zinc-600">{formatDate(room.created_at)} 创建</div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {confirmDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <button
            type="button"
            className="absolute inset-0 bg-black/70"
            aria-label="关闭确认弹窗"
            onClick={() => {
              if (!deletingAccount) setConfirmAction(null)
            }}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="profile-confirm-title"
            className="relative w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-2xl shadow-black/60"
          >
            <h3 id="profile-confirm-title" className="text-lg font-semibold text-zinc-100">
              {confirmDialog.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-zinc-400">{confirmDialog.description}</p>
            <div className="mt-6 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setConfirmAction(null)}
                disabled={deletingAccount}
                className="h-9 rounded-lg border border-zinc-800 px-4 text-sm text-zinc-300 transition hover:border-zinc-600 disabled:cursor-not-allowed disabled:text-zinc-700"
              >
                取消
              </button>
              <button
                type="button"
                onClick={handleConfirmAction}
                disabled={confirmAction === 'delete' && deletingAccount}
                className={`h-9 rounded-lg px-4 text-sm font-semibold transition active:scale-[0.98] disabled:cursor-not-allowed ${
                  confirmDialog.danger
                    ? 'bg-red-500 text-white hover:bg-red-400 disabled:bg-red-950 disabled:text-red-900'
                    : 'bg-zinc-100 text-black hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600'
                }`}
              >
                {confirmDialog.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}
