/** 生成、预览和下载当前用户的会员分享卡片。 */
import { useEffect, useState } from 'react'
import type { User } from '@/types/user'
import {
  profileCardThemes,
  renderProfileCard,
  type ProfileCardTheme,
} from './profileShareCardRenderer'
import { formatProfileDate } from './profilePageModel'

/** 可供生成按钮随机选择的底图键。 */
const profileCardThemeKeys = Object.keys(
  profileCardThemes,
) as ProfileCardTheme[]

/** 一次分享卡片渲染的结果或错误。 */
type ProfileCardRenderResult = {
  /** 参与本次渲染的用户对象。 */
  user: User
  /** 本次渲染的底图。 */
  theme: ProfileCardTheme
  /** 用于区分同一用户和底图的连续渲染请求。 */
  revision: number
  /** 成功时可预览和下载的 PNG 数据 URL。 */
  imageUrl?: string
  /** 失败时用于界面提示的错误原因。 */
  error?: string
}

/** 展示并导出使用已保存资料生成的会员分享卡片。 */
type ProfileShareCardProps = {
  /** 当前已保存的用户资料。 */
  user: User | null
}

/** 展示并导出使用已保存资料生成的会员分享卡片。
 * @param user - 当前已保存的用户资料。
 * @returns 会员卡片预览、生成和下载控件。
 */
export function ProfileShareCard({ user }: ProfileShareCardProps) {
  const [theme, setTheme] = useState<ProfileCardTheme>('celty')
  const [revision, setRevision] = useState(0)
  const [result, setResult] = useState<ProfileCardRenderResult>()
  const currentResult =
    result?.user === user &&
    result.theme === theme &&
    result.revision === revision
      ? result
      : undefined
  const imageUrl = currentResult?.imageUrl ?? ''
  const loading = Boolean(user) && !currentResult
  const error = user ? (currentResult?.error ?? '') : '无法读取当前账号资料。'

  useEffect(() => {
    let cancelled = false
    if (!user) return

    renderProfileCard(user, theme).then(
      (dataUrl) => {
        if (cancelled) return
        setResult({ user, theme, revision, imageUrl: dataUrl })
      },
      (cause: unknown) => {
        if (cancelled) return
        console.error('分享卡片生成失败。', cause)
        const detail = cause instanceof Error ? `：${cause.message}` : ''
        setResult({
          user,
          theme,
          revision,
          error: `分享卡片生成失败${detail}，请重试。`,
        })
      },
    )

    return () => {
      cancelled = true
    }
  }, [user, theme, revision])

  /** 随机选择一款底图，并重新渲染当前已保存的资料。 */
  function handleGenerate() {
    const nextTheme =
      profileCardThemeKeys[
        Math.floor(Math.random() * profileCardThemeKeys.length)
      ]
    setTheme(nextTheme)
    setRevision((current) => current + 1)
  }

  /** 将当前预览的数据 URL 作为 PNG 下载。 */
  function handleDownload() {
    if (!imageUrl || !user) return
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = `member-card-${user.id}.png`
    link.click()
  }

  return (
    <section className="relative mx-auto max-w-5xl">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">个人资料</h1>
          <p className="mt-2 text-sm text-zinc-400">
            分享你的会员卡片。每次生成都会随机选择六款底图之一。
          </p>
        </div>
      </div>

      <div className="overflow-hidden border border-zinc-700 bg-black">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={`会员分享卡片预览：${profileCardThemes[theme].label}`}
            className="block h-auto w-full"
          />
        ) : (
          <div
            className="flex aspect-[3/2] items-center justify-center bg-zinc-950 text-sm text-zinc-400"
            aria-hidden="true"
          >
            {loading ? '正在生成分享卡片…' : '分享卡片暂不可用'}
          </div>
        )}
      </div>
      {user && (
        <dl className="sr-only" aria-label="分享卡片文字内容">
          <dt>昵称</dt>
          <dd>
            {user.nickname?.replace(/\s+/g, ' ').trim() ||
              user.username.replace(/\s+/g, ' ').trim()}
          </dd>
          <dt>用户名</dt>
          <dd>@{user.username.replace(/\s+/g, ' ').trim()}</dd>
          <dt>成员编号</dt>
          <dd>{String(user.id).padStart(6, '0')}</dd>
          <dt>加入日期</dt>
          <dd>{formatProfileDate(user.created_at)}</dd>
          <dt>个人简介</dt>
          <dd>{user.bio?.trim() || '尚未填写个人简介'}</dd>
        </dl>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleGenerate}
          disabled={loading || !user}
          className="rounded-sm border border-zinc-200 px-5 py-2 text-sm hover:bg-zinc-100 hover:text-black disabled:cursor-not-allowed disabled:opacity-40"
        >
          生成分享卡片
        </button>
        <button
          type="button"
          onClick={handleDownload}
          disabled={loading || !imageUrl}
          className="rounded-sm border border-zinc-700 px-5 py-2 text-sm text-zinc-200 hover:border-zinc-400 disabled:cursor-not-allowed disabled:opacity-40"
        >
          下载 PNG
        </button>
        <span className="text-sm text-zinc-400">
          当前底图：{profileCardThemes[theme].label}
        </span>
      </div>
      <p className="sr-only" role="status" aria-live="polite">
        {loading ? '正在生成分享卡片。' : imageUrl ? '分享卡片已就绪。' : ''}
      </p>
      {error && (
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <p role="alert" className="text-sm text-red-300">
            {error}
          </p>
          <button
            type="button"
            onClick={() => setRevision((current) => current + 1)}
            disabled={loading || !user}
            className="text-sm text-zinc-300 underline underline-offset-4 hover:text-white disabled:opacity-40"
          >
            重试生成
          </button>
        </div>
      )}
    </section>
  )
}
