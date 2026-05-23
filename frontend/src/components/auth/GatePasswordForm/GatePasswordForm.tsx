/**
 * @parm 组件用途：展示门禁密码输入表单。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { FormEvent } from 'react'

interface GatePasswordFormProps {
  password: string
  onPasswordChange: (password: string) => void
  onSubmit: (event: FormEvent) => void
}

export default function GatePasswordForm({ password, onPasswordChange, onSubmit }: GatePasswordFormProps) {
  return (
    <form onSubmit={onSubmit}>
      <AuthTextInput
        type="password"
        value={password}
        onChange={(event) => onPasswordChange(event.target.value)}
        placeholder="Password"
        className="mx-auto mt-2 h-7 w-full rounded-3xl border-0 bg-[#666] px-4 text-black placeholder:text-sm placeholder-gray-800 focus:bg-white focus:ring-2"
        autoComplete="current-password"
      />
    </form>
  )
}
