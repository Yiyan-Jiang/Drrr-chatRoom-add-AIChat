/**
 * 展示退出登录或注销账号前的确认弹窗。
 */
import type { ConfirmDialogModel } from './profilePageModel'

/** 账号操作确认框的文案、状态和回调。 */
type ConfirmActionDialogProps = {
  /** 确认框文案与危险操作样式标记。 */
  dialog: ConfirmDialogModel
  /** 是否正在注销，用于禁用关闭和取消入口。 */
  deletingAccount: boolean
  /** 是否禁用确认按钮。 */
  confirmingDelete: boolean
  /** 取消待确认操作并关闭弹窗。 */
  onCancel: () => void
  /** 确认当前账号操作。 */
  onConfirm: () => void
}

/** 展示退出登录或注销账号确认框，根据请求状态禁用相关操作。 */
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
        className="absolute inset-0 bg-black/75"
        aria-label="关闭确认弹窗"
        onClick={() => {
          if (!deletingAccount) onCancel()
        }}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-confirm-title"
        className="relative w-full max-w-md rounded-sm border border-zinc-700 bg-black p-6 shadow-2xl shadow-black/60"
      >
        <h3
          id="profile-confirm-title"
          className="text-lg font-semibold text-zinc-100"
        >
          {dialog.title}
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-zinc-400">
          {dialog.description}
        </p>
        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={deletingAccount}
            className="h-9 rounded-sm border border-zinc-700 px-4 text-sm text-zinc-300 transition hover:border-zinc-400 disabled:cursor-not-allowed disabled:text-zinc-700"
          >
            取消
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={confirmingDelete}
            className={`h-9 rounded-sm border px-4 text-sm font-semibold transition disabled:cursor-not-allowed ${
              dialog.danger
                ? 'border-red-700 text-red-200 hover:bg-red-950 disabled:border-red-950 disabled:text-red-900'
                : 'border-zinc-200 text-zinc-100 hover:bg-zinc-100 hover:text-black disabled:border-zinc-800 disabled:text-zinc-600'
            }`}
          >
            {dialog.confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
