/** 展示账号信息，并复用现有退出登录与注销流程。 */
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { usersApi } from '@/api/users'
import {
  buildConfirmDialog,
  ConfirmActionDialog,
  formatProfileDate,
  type ConfirmAction,
} from '@/components/profile'
import { useAuth } from '@/contexts/AuthContext'

/** 管理账号操作，注销成功后清理会话并返回登录页。 */
export default function SettingsPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')
  const dialog = buildConfirmDialog(confirmAction, deleting)

  useEffect(() => {
    if (!confirmAction) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !deleting) setConfirmAction(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [confirmAction, deleting])

  /** 执行已确认的操作，仅在删除成功后清理当前会话。 */
  async function handleConfirm() {
    if (confirmAction === 'logout') {
      logout()
      navigate('/login', { replace: true })
      return
    }
    if (confirmAction !== 'delete' || !user || deleting) return
    setDeleting(true)
    setError('')
    try {
      await usersApi.delete(user.id)
      logout()
      navigate('/login', { replace: true })
    } catch {
      setError('注销账号失败，请稍后重试。')
    } finally {
      setDeleting(false)
      setConfirmAction(null)
    }
  }

  return (
    <div className="h-full overflow-auto bg-black px-4 py-7 text-zinc-100 sm:px-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <header>
          <h1 className="text-2xl font-semibold">设定</h1>
          <p className="mt-2 text-sm text-zinc-400">
            查看账号信息和管理当前登录。
          </p>
        </header>
        <section className="rounded-sm border border-zinc-700 p-5 sm:p-6">
          <h2 className="text-base font-semibold">账号信息</h2>
          <dl className="mt-4 space-y-4 text-sm">
            <div className="flex flex-wrap justify-between gap-2">
              <dt className="text-zinc-400">用户名</dt>
              <dd className="break-all">{user?.username}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-zinc-400">用户 ID</dt>
              <dd>{user?.id}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-zinc-400">注册日期</dt>
              <dd>{formatProfileDate(user?.created_at)}</dd>
            </div>
          </dl>
          <Link
            to="/profile"
            className="mt-5 inline-block text-sm underline underline-offset-4 hover:text-zinc-300"
          >
            编辑个人资料
          </Link>
        </section>
        <section className="rounded-sm border border-zinc-700 p-5 sm:p-6">
          <h2 className="text-base font-semibold">当前登录</h2>
          <p className="mt-2 text-sm text-zinc-400">
            退出后需要重新登录才能使用聊天室。
          </p>
          <button
            type="button"
            onClick={() => {
              setError('')
              setConfirmAction('logout')
            }}
            disabled={deleting}
            className="mt-4 rounded-sm border border-zinc-500 px-4 py-2 text-sm hover:bg-zinc-100 hover:text-black disabled:opacity-40"
          >
            退出登录
          </button>
        </section>
        <section
          className="rounded-sm border border-red-950 p-5 sm:p-6"
          aria-busy={deleting}
        >
          <h2 className="text-base font-semibold text-red-200">注销账号</h2>
          <p className="mt-2 text-sm text-zinc-400">
            账号资料会被删除，此操作不可恢复。
          </p>
          <button
            type="button"
            onClick={() => {
              setError('')
              setConfirmAction('delete')
            }}
            disabled={deleting}
            className="mt-4 rounded-sm border border-red-800 px-4 py-2 text-sm text-red-300 hover:bg-red-950 disabled:opacity-40"
          >
            {deleting ? '注销中…' : '注销账号'}
          </button>
        </section>
        {error && (
          <p role="alert" className="text-sm text-red-300">
            {error}
          </p>
        )}
        {dialog && (
          <ConfirmActionDialog
            dialog={dialog}
            deletingAccount={deleting}
            confirmingDelete={deleting}
            onCancel={() => setConfirmAction(null)}
            onConfirm={handleConfirm}
          />
        )}
      </div>
    </div>
  )
}
