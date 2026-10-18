/**
 * 普通聊天室的消息编辑与发送入口。
 */
import type { FormEvent } from 'react'

/** 消息输入区的受控内容、交互状态和提交回调。 */
interface ChatComposerProps {
  /** 当前输入内容，由父组件维护。 */
  value: string
  /** 同时禁用文本输入和发送按钮。 */
  disabled?: boolean
  /** 将编辑后的完整内容交给父组件。 */
  onChange: (value: string) => void
  /** 提交当前消息；消息发送和结果处理由父组件负责。 */
  onSubmit: () => void
}

/** 展示消息输入框，并在禁用或内容仅含空白时禁用发送按钮。 */
export default function ChatComposer({
  value,
  disabled,
  onChange,
  onSubmit,
}: ChatComposerProps) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    onSubmit()
  }

  return (
    <form className="flex flex-col gap-2" onSubmit={handleSubmit}>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        rows={3}
        className="min-h-20 w-100 self-center resize-none rounded-2xl border bg-[#39393E] border-[#4D4D4D] px-3 py-2 text-sm text-zinc-100 outline-none focus:border-white disabled:opacity-60"
        placeholder="输入消息..."
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="h-7 w-50 self-center rounded-3xl bg-[#4D4D4D] px-5 text-sm font-semibold text-[#969696] transition hover:border-white hover:border hover:text-white disabled:cursor-not-allowed "
      >
        post!
      </button>
    </form>
  )
}
