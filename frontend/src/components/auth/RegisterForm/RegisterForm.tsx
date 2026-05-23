/**
 * @parm 组件用途：展示注册表单并把输入和提交事件交给上层。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { RegisterRequest } from '@/types/chat'
import type { ChangeEvent, FormEvent } from 'react'

interface RegisterFormProps {
  form: RegisterRequest
  confirmPassword: string
  loading: boolean
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  onConfirmChange: (event: ChangeEvent<HTMLInputElement>) => void
  onSubmit: (event: FormEvent) => void
}

export default function RegisterForm({
  form,
  confirmPassword,
  loading,
  onChange,
  onConfirmChange,
  onSubmit,
}: RegisterFormProps) {
  return (
    <form onSubmit={onSubmit} className="space-y-3">
      <div className="flex">
        <AuthTextInput
          id="username"
          name="username"
          required
          value={form.username}
          onChange={onChange}
          className="mx-auto mt-2 h-7 w-[80%] rounded-3xl border-0 bg-[#666] px-4 text-black placeholder:text-sm placeholder-gray-800 focus:bg-white focus:ring-2"
          placeholder="Username"
          disabled={loading}
        />
      </div>

      <div className="flex">
        <AuthTextInput
          id="password"
          name="password"
          type="password"
          required
          value={form.password}
          onChange={onChange}
          className="mx-auto h-7 w-[80%] rounded-3xl border-0 bg-[#666] px-4 text-black placeholder:text-sm placeholder-gray-800 focus:bg-white focus:ring-2"
          placeholder="Password"
          disabled={loading}
        />
      </div>

      <div className="flex">
        <AuthTextInput
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          required
          value={confirmPassword}
          onChange={onConfirmChange}
          className="mx-auto h-7 w-[80%] rounded-3xl border-0 bg-[#666] px-4 text-black placeholder:text-sm placeholder-gray-800 focus:bg-white focus:ring-2"
          placeholder="Password Again"
          disabled={loading}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-3 h-7 w-full cursor-pointer rounded-3xl border-3 border-white bg-[#666] px-4 font-semibold text-white active:scale-95 active:border-0 active:text-black disabled:opacity-50"
      >
        {loading ? 'Waiting...' : 'Register'}
      </button>
    </form>
  )
}
