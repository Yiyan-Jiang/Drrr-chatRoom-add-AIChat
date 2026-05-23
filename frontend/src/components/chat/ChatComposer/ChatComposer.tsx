/**
 * @parm 组件用途：展示普通聊天室的消息输入和发送区域。
 */
import type { FormEvent } from 'react'

interface ChatComposerProps {
  value: string
  disabled?: boolean
  onChange: (value: string) => void
  onSubmit: () => void
}

export default function ChatComposer({ value, disabled, onChange, onSubmit }: ChatComposerProps) {
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
