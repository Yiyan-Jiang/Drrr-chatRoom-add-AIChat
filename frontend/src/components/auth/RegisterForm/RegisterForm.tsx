/**
 * 展示注册表单并把输入和提交事件交给上层。
 */
import AuthTextInput from '@/components/auth/AuthTextInput'
import type { RegisterRequest } from '@/types/auth'
import type { ChangeEvent, FormEvent } from 'react'

/** 注册表单字段与提交回调。 */
interface RegisterFormProps {
  /** 当前注册凭据。 */
  form: RegisterRequest
  /** 用于二次确认的密码输入。 */
  confirmPassword: string
  /** 请求中标记，用于禁用输入和提交。 */
  loading: boolean
  /** 接收用户名或密码字段变更。 */
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  /** 接收确认密码字段变更。 */
  onConfirmChange: (event: ChangeEvent<HTMLInputElement>) => void
  /** 接收表单提交事件，密码一致性检查由调用方负责。 */
  onSubmit: (event: FormEvent) => void
}

/** 展示注册凭据和确认密码输入，把校验与提交处理交给调用方。 */
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
