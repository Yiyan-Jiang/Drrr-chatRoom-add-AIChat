/**
 * @parm 组件用途：展示并编辑用户头像、昵称、简介和账号操作入口。
 */
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
  const avatarAssets = resolveChatAvatarAssets(form.avatarKey || user?.avatar_key)

  return (
    <section className="flex items-start justify-between gap-5">
      <div className="flex min-w-0 items-start gap-5">
        <div className="relative shrink-0">
          <button
            type="button"
            onClick={() => onPickerOpenChange(!pickerOpen)}
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
              <div className="fixed inset-0 z-10" onClick={() => onPickerOpenChange(false)} />
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
                          onFormChange({ ...form, avatarKey: key })
                          onPickerOpenChange(false)
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
              onChange={(event) => onFormChange({ ...form, nickname: event.target.value })}
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
                  onChange={(event) => onFormChange({ ...form, bio: event.target.value })}
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
              onClick={onSave}
              className="h-9 rounded-lg bg-zinc-100 px-5 text-sm font-semibold text-black transition active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-600"
            >
              {saving ? '保存中...' : '保存'}
            </button>
            <button
              type="button"
              disabled={saving || deletingAccount}
              onClick={onCancelEdit}
              className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-600 disabled:cursor-not-allowed disabled:text-zinc-700"
            >
              取消
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={onStartEdit}
            disabled={deletingAccount}
            className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100"
          >
            编辑
          </button>
        )}
        <button
          type="button"
          onClick={onLogout}
          disabled={saving || deletingAccount}
          className="h-9 rounded-lg border border-zinc-800 px-5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:text-zinc-700"
        >
          退出登录
        </button>
        <button
          type="button"
          onClick={onDeleteAccount}
          disabled={!user || saving || deletingAccount}
          className="h-9 rounded-lg border border-red-900/70 px-5 text-sm text-red-300 transition hover:border-red-500 hover:text-red-100 disabled:cursor-not-allowed disabled:border-zinc-800 disabled:text-zinc-700"
        >
          {deletingAccount ? '注销中...' : '注销账号'}
        </button>
      </div>
    </section>
  )
}
