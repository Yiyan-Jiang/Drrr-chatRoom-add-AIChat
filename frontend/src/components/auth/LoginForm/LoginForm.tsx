/**
 * 展示登录表单并把输入和提交事件交给上层。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { LoginCredentials } from '@/types/auth'
import type { ChangeEvent, FormEvent } from 'react'

/** 登录表单字段、加载状态和交互回调。 */
interface LoginFormProps {
  /** 当前用户名和密码。 */
  form: LoginCredentials
  /** 请求中标记，用于禁用输入和提交。 */
  loading: boolean
  /** 当前聚焦的字段名，无焦点时为 null。 */
  focusedField: string | null
  /** 接收字段变更事件，通过 name 区分字段。 */
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  /** 接收获得焦点的字段名。 */
  onFocus: (fieldName: string) => void
  /** 字段失去焦点时调用。 */
  onBlur: () => void
  /** 接收表单提交事件，认证由调用方负责。 */
  onSubmit: (event: FormEvent) => void
}

/** 展示用户名和密码输入，加载期间禁用输入与登录按钮。 */
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
            focusedField === 'username'
              ? 'bg-gray-800 focus:bg-amber-50'
              : 'bg-[#666] placeholder-[#333]'
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
            focusedField === 'password'
              ? 'bg-gray-800 focus:bg-amber-50'
              : 'bg-[#666] placeholder-[#333]'
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
