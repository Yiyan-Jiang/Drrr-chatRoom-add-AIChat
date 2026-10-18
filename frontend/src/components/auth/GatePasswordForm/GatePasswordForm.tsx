/**
 * 展示门禁密码输入表单。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { FormEvent } from 'react'

/** 门禁密码表单的受控值与提交事件。 */
interface GatePasswordFormProps {
  /** 当前门禁密码输入。 */
  password: string
  /** 接收新的密码内容。 */
  onPasswordChange: (password: string) => void
  /** 接收原生提交事件，默认行为由调用方处理。 */
  onSubmit: (event: FormEvent) => void
}

/** 展示门禁密码输入框，并把表单提交事件交给调用方。 */
export default function GatePasswordForm({
  password,
  onPasswordChange,
  onSubmit,
}: GatePasswordFormProps) {
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
