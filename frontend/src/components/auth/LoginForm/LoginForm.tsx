/**
 * @parm 组件用途：展示登录表单并把输入和提交事件交给上层。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { LoginCredentials } from '@/types/auth'
import type { ChangeEvent, FormEvent } from 'react'

interface LoginFormProps {
  form: LoginCredentials
  loading: boolean
  focusedField: string | null
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  onFocus: (fieldName: string) => void
  onBlur: () => void
  onSubmit: (event: FormEvent) => void
}

export default function LoginForm({
  form,
  loading,
  focusedField,
  onChange,
  onFocus,
  onBlur,
  onSubmit,
}: LoginFormProps) {
  return (
    <form onSubmit={onSubmit} className="bottom-0 space-y-2">
      <div className="flex">
        <AuthTextInput
          id="username"
          name="username"
          required
          value={form.username}
          onChange={onChange}
          onFocus={() => onFocus('username')}
          onBlur={onBlur}
          className={`mx-auto mt-3 h-6 w-[80%] rounded-3xl border px-4 text-sm text-black placeholder:text-sm transition-colors focus:outline-none focus:ring-2 ${
            focusedField === 'username' ? 'bg-gray-800 focus:bg-amber-50' : 'bg-[#666] placeholder-[#333]'
          } ${loading ? 'cursor-not-allowed opacity-50' : ''}`}
          placeholder="Username"
          disabled={loading}
          autoComplete="username"
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
          onFocus={() => onFocus('password')}
          onBlur={onBlur}
          className={`mx-auto h-6 w-[80%] rounded-3xl border px-4 text-black placeholder:text-sm transition-colors focus:outline-none focus:ring-2 ${
            focusedField === 'password' ? 'bg-gray-800 focus:bg-amber-50' : 'bg-[#666] placeholder-[#333]'
          } ${loading ? 'cursor-not-allowed opacity-50' : ''}`}
          placeholder="Password"
          disabled={loading}
          autoComplete="current-password"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-3 h-7 w-full cursor-pointer rounded-3xl border-3 border-white bg-[#666] px-4 font-semibold text-white active:scale-95 active:border-0 active:text-black disabled:opacity-50"
      >
        {loading ? 'Wait...' : 'ENTER'}
      </button>
    </form>
  )
}
