/**
 * @parm 组件用途：展示并编辑当前用户的头像、昵称、简介和账号操作入口。
 */
import { useEffect, useState } from 'react'
import { chatAvatarCatalog, resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { User } from '@/types/chat'
import type { ProfileForm } from './profilePageModel'

type ProfileHeaderProps = {
  user: User | null
  form: ProfileForm
  displayName: string
  editing: boolean
  pickerOpen: boolean
  saving: boolean
  deletingAccount: boolean
  canSave: boolean
  onFormChange: (form: ProfileForm) => void
  onPickerOpenChange: (open: boolean) => void
  onStartEdit: () => void
  onCancelEdit: () => void
  onSave: () => void
  onLogout: () => void
  onDeleteAccount: () => void
}

export function ProfileHeader({
  user,
  form,
  displayName,
  editing,
  pickerOpen,
  saving,
  deletingAccount,
  canSave,
  onFormChange,
  onPickerOpenChange,
  onStartEdit,
  onCancelEdit,
  onSave,
  onLogout,
  onDeleteAccount,
}: ProfileHeaderProps) {
  const [accountMenuOpen, setAccountMenuOpen] = useState(false)
  const avatarAssets = resolveChatAvatarAssets(form.avatarKey || user?.avatar_key)

  useEffect(() => {
    if (!accountMenuOpen) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setAccountMenuOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [accountMenuOpen])

  const handleLogout = () => {
    setAccountMenuOpen(false)
    onLogout()
  }

  const handleDeleteAccount = () => {
    setAccountMenuOpen(false)
    onDeleteAccount()
  }

  return (
    <section className="flex min-w-0 flex-col gap-5 sm:flex-row sm:items-center">
      <div className="relative shrink-0">
        <button
          type="button"
          onClick={() => onPickerOpenChange(!pickerOpen)}
          disabled={!editing}
          className="group relative block h-36 w-36 overflow-hidden rounded-full border-4 border-zinc-200 bg-zinc-950 transition enabled:hover:border-white disabled:cursor-default"
          aria-label="更换头像"
        >
          <img src={avatarAssets.avatar} alt="用户头像" className="h-full w-full object-cover" />
          {editing && (
            <span className="absolute inset-x-0 bottom-0 bg-black/70 py-2 text-center text-xs font-medium text-zinc-100 opacity-0 transition group-hover:opacity-100">
              更换
            </span>
          )}
        </button>

        {pickerOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => onPickerOpenChange(false)} />
            <div className="absolute left-0 top-[calc(100%+0.75rem)] z-20 w-64 rounded-sm border border-zinc-700 bg-black p-3 shadow-xl shadow-black/60">
              <p className="mb-2 px-1 text-[11px] font-medium uppercase text-zinc-500">选择头像</p>
              <div className="grid grid-cols-4 gap-2">
                {Object.entries(chatAvatarCatalog).map(([key, assets]) => {
                  const selected = key === form.avatarKey
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => {
                        onFormChange({ ...form, avatarKey: key })
                        onPickerOpenChange(false)
                      }}
                      className={`overflow-hidden rounded-sm border transition ${
                        selected ? 'border-zinc-100 ring-1 ring-zinc-100' : 'border-zinc-800 hover:border-zinc-500'
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
        <div className="flex flex-wrap items-center gap-3">
          {editing ? (
            <input
              value={form.nickname}
              maxLength={64}
              autoFocus
              onChange={(event) => onFormChange({ ...form, nickname: event.target.value })}
              className="h-10 min-w-0 max-w-xs rounded-sm border border-zinc-700 bg-black px-3 text-2xl font-semibold text-zinc-100 outline-none transition focus:border-zinc-300"
            />
          ) : (
            <h1 className="truncate text-3xl font-semibold tracking-normal text-zinc-100">{displayName}</h1>
          )}
        </div>

        <p className="block border-b border-gray-200 pb-2 w-30 mt-3 font-mono text-sm text-zinc-300">@{user?.username || '-'} ID: {user?.id ?? '-'}</p>

        <div className="mt-3">
          {editing ? (
            <>
              <div className="mb-1.5 flex max-w-xl items-center justify-between text-xs text-zinc-500">
                <span>简介</span>
                <span className="font-mono tabular-nums text-zinc-600">{form.bio.length}/200</span>
              </div>
              <textarea
                value={form.bio}
                maxLength={200}
                rows={4}
                onChange={(event) => onFormChange({ ...form, bio: event.target.value })}
                className="w-full max-w-xl resize-none rounded-sm border border-zinc-700 bg-black px-3.5 py-2.5 text-sm leading-relaxed text-zinc-100 outline-none transition focus:border-zinc-300"
              />
            </>
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">
              {user?.bio?.trim() || '夜晚很安静，想和某个人聊聊天。'}
            </p>
          )}
        </div>

        <div className="mt-5 flex w-full flex-wrap items-center gap-2">
          {editing ? (
            <>
              <button
                type="button"
                disabled={!canSave}
                onClick={onSave}
                className="h-9 min-w-[8rem] rounded-sm border border-zinc-200 px-5 text-sm font-semibold text-zinc-100 transition hover:bg-zinc-100 hover:text-black disabled:cursor-not-allowed disabled:border-zinc-800 disabled:text-zinc-600"
              >
                {saving ? '保存中...' : '保存'}
              </button>
              <button
                type="button"
                disabled={saving || deletingAccount}
                onClick={onCancelEdit}
                className="h-9 min-w-[8rem] rounded-sm border border-zinc-700 px-5 text-sm text-zinc-300 transition hover:border-zinc-400 disabled:cursor-not-allowed disabled:text-zinc-700"
              >
                取消
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={onStartEdit}
              disabled={deletingAccount}
              className="h-9 min-w-[9rem] rounded-sm border border-zinc-500 px-5 text-sm font-semibold text-zinc-100 transition hover:bg-zinc-100 hover:text-black disabled:cursor-not-allowed disabled:text-zinc-700"
            >
              编辑资料
            </button>
          )}

          <div className="relative">
            <button
              type="button"
              aria-label="更多账号操作"
              aria-expanded={accountMenuOpen}
              onClick={() => setAccountMenuOpen((open) => !open)}
              disabled={saving || deletingAccount}
              className="h-9 w-9 rounded-sm border border-zinc-700 text-lg leading-none text-zinc-300 transition hover:border-zinc-400 hover:text-zinc-100 disabled:cursor-not-allowed disabled:text-zinc-700"
            >
              ...
            </button>

            {accountMenuOpen && (
              <>
                <button
                  type="button"
                  aria-label="关闭账号操作菜单"
                  className="fixed inset-0 z-10 cursor-default bg-transparent"
                  onClick={() => setAccountMenuOpen(false)}
                />
                <div className="account-actions-menu absolute left-0 top-[calc(100%+0.5rem)] z-20 w-40 rounded-sm border border-zinc-700 bg-black p-1 shadow-xl shadow-black/60 sm:left-auto sm:right-0">
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="block h-9 w-full rounded-sm px-3 text-left text-sm text-zinc-300 transition hover:bg-zinc-900 hover:text-white"
                  >
                    退出登录
                  </button>
                  <button
                    type="button"
                    onClick={handleDeleteAccount}
                    disabled={!user}
                    className="block h-9 w-full rounded-sm px-3 text-left text-sm text-red-300 transition hover:bg-red-950/50 hover:text-red-100 disabled:cursor-not-allowed disabled:text-zinc-700"
                  >
                    注销账号
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
