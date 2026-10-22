/** 编辑当前账号的公开资料，并同步认证上下文。 */
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { usersApi } from '@/api/users'
import {
  chatAvatarCatalog,
  resolveChatAvatarAssets,
} from '@/assets/chatAvatarCatalog'
import { toProfileForm } from '@/components/profile'
import { useAuth } from '@/contexts/AuthContext'

/** 编辑昵称、简介与内置头像，保存失败时保留输入。 */
export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState(() => toProfileForm(user))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  const original = toProfileForm(user)
  const changed =
    form.nickname.trim() !== original.nickname ||
    form.bio !== original.bio ||
    form.avatarKey !== original.avatarKey

  /** 提交资料，在成功后更新全局用户信息。 */
  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSaved(false)
    const nickname = form.nickname.trim()
    if (!nickname || nickname.length > 64 || form.bio.length > 200) {
      setError('请填写 1–64 字的昵称，简介最多 200 字。')
      return
    }
    setSaving(true)
    try {
      const updated = await usersApi.updateMe({
        nickname,
        bio: form.bio,
        ...(form.avatarKey ? { avatar_key: form.avatarKey } : {}),
      })
      updateUser(updated)
      setForm(toProfileForm(updated))
      setSaved(true)
    } catch {
      setError('保存失败，请稍后重试。你的修改仍保留在表单中。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="h-full overflow-auto bg-black px-4 py-7 text-zinc-100 sm:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-2xl font-semibold">个人资料</h1>
        <p className="mt-2 text-sm text-zinc-400">
          设置其他成员看到的昵称、简介和头像。
        </p>
        <form
          onSubmit={handleSave}
          aria-busy={saving}
          className="mt-6 space-y-6 rounded-sm border border-zinc-700 p-5 sm:p-6"
        >
          <fieldset disabled={saving} className="space-y-6 disabled:opacity-60">
            <legend className="sr-only">编辑个人资料</legend>
            <div className="flex items-center gap-4">
              <img
                src={resolveChatAvatarAssets(form.avatarKey).avatar}
                alt="当前头像预览"
                className="h-20 w-20 rounded-full border border-zinc-600 object-cover"
              />
              <p className="min-w-0 break-all text-sm text-zinc-400">
                @{user?.username}
              </p>
            </div>
            <fieldset>
              <legend className="mb-3 text-sm font-medium">选择内置头像</legend>
              <div className="grid grid-cols-4 gap-3 sm:grid-cols-8">
                {Object.entries(chatAvatarCatalog).map(([key, assets]) => (
                  <label
                    key={key}
                    className="cursor-pointer text-center text-xs text-zinc-400"
                  >
                    <input
                      type="radio"
                      name="avatar"
                      value={key}
                      checked={form.avatarKey === key}
                      onChange={() => {
                        setForm({ ...form, avatarKey: key })
                        setSaved(false)
                      }}
                      className="peer sr-only"
                    />
                    <img
                      src={assets.avatar}
                      alt=""
                      className="mx-auto h-12 w-12 rounded-sm border border-zinc-700 object-cover peer-checked:border-white peer-checked:ring-1 peer-checked:ring-white peer-focus-visible:outline-2 peer-focus-visible:outline-offset-4 peer-focus-visible:outline-white"
                    />
                    <span className="mt-2 block">{key}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            <div>
              <label
                htmlFor="profile-nickname"
                className="mb-2 block text-sm font-medium"
              >
                昵称
              </label>
              <input
                id="profile-nickname"
                value={form.nickname}
                required
                maxLength={64}
                onChange={(event) => {
                  setForm({ ...form, nickname: event.target.value })
                  setSaved(false)
                }}
                className="w-full rounded-sm border border-zinc-700 bg-black px-3 py-2 text-sm focus:border-zinc-300 focus:outline-none"
              />
            </div>
            <div>
              <label
                htmlFor="profile-bio"
                className="mb-2 block text-sm font-medium"
              >
                简介
              </label>
              <textarea
                id="profile-bio"
                value={form.bio}
                maxLength={200}
                rows={5}
                aria-describedby="profile-bio-limit"
                onChange={(event) => {
                  setForm({ ...form, bio: event.target.value })
                  setSaved(false)
                }}
                className="w-full resize-y rounded-sm border border-zinc-700 bg-black px-3 py-2 text-sm focus:border-zinc-300 focus:outline-none"
              />
              <p
                id="profile-bio-limit"
                className="mt-1 text-right text-xs text-zinc-400"
              >
                {form.bio.length}/200
              </p>
            </div>
          </fieldset>
          {error && (
            <p role="alert" className="text-sm text-red-300">
              {error}
            </p>
          )}
          <p role="status" className="text-sm text-zinc-300">
            {saving ? '正在保存资料…' : saved ? '资料已保存。' : ''}
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={saving || !changed}
              className="rounded-sm border border-zinc-200 px-5 py-2 text-sm hover:bg-zinc-100 hover:text-black disabled:cursor-not-allowed disabled:opacity-40"
            >
              {saving ? '保存中…' : '保存资料'}
            </button>
            <button
              type="button"
              disabled={saving || !changed}
              onClick={() => {
                setForm(toProfileForm(user))
                setError('')
                setSaved(false)
              }}
              className="rounded-sm border border-zinc-700 px-5 py-2 text-sm text-zinc-300 hover:border-zinc-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              重置修改
            </button>
          </div>
        </form>
        <Link
          to="/my"
          className="mt-5 inline-block text-sm text-zinc-400 underline underline-offset-4 hover:text-white"
        >
          返回我的页面
        </Link>
      </div>
    </div>
  )
}
