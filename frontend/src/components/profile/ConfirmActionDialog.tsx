/**
 * @parm 组件用途：展示退出登录或注销账号前的确认弹窗。
 */
import type { ConfirmDialogModel } from './profilePageModel'

type ConfirmActionDialogProps = {
  dialog: ConfirmDialogModel
  deletingAccount: boolean
  confirmingDelete: boolean
  onCancel: () => void
  onConfirm: () => void
}

export function ConfirmActionDialog({
  dialog,
  deletingAccount,
  confirmingDelete,
  onCancel,
  onConfirm,
}: ConfirmActionDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/70"
        aria-label="关闭确认弹窗"
        onClick={() => {
          if (!deletingAccount) onCancel()
        }}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-confirm-title"
        className="relative w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-2xl shadow-black/60"
      >
        <h3 id="profile-confirm-title" className="text-lg font-semibold text-zinc-100">
          {dialog.title}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-zinc-400">{dialog.description}</p>
        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={deletingAccount}
            className="h-9 rounded-lg border border-zinc-800 px-4 text-sm text-zinc-300 transition hover:border-zinc-600 disabled:cursor-not-allowed disabled:text-zinc-700"
          >
            取消
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={confirmingDelete}
            className={`h-9 rounded-lg px-4 text-sm font-semibold transition active:scale-[0.98] disabled:cursor-not-allowed ${
              dialog.danger
                ? 'bg-red-500 text-white hover:bg-red-400 disabled:bg-red-950 disabled:text-red-900'
                : 'bg-zinc-100 text-black hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600'
            }`}
          >
            {dialog.confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
