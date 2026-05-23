/**
 * @parm 组件用途：封装认证表单里复用的输入框。
 */
import type { ChangeEvent } from 'react'

interface AuthTextInputProps {
  id?: string
  name?: string
  type?: string
  value: string
  placeholder: string
  disabled?: boolean
  required?: boolean
  autoComplete?: string
  focused?: boolean
  className?: string
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  onFocus?: () => void
  onBlur?: () => void
}

export default function AuthTextInput({
  id,
  name,
  type = 'text',
  value,
  placeholder,
  disabled,
  required,
  autoComplete,
  focused,
  className,
  onChange,
  onFocus,
  onBlur,
}: AuthTextInputProps) {
  const focusClass =
    focused === undefined
      ? 'bg-[#666] placeholder-gray-800 focus:bg-white'
      : focused
        ? 'bg-gray-800 focus:bg-amber-50'
        : 'bg-[#666] placeholder-[#333]'

  return (
    <input
      id={id}
      name={name}
      type={type}
      required={required}
      value={value}
      onChange={onChange}
      onFocus={onFocus}
      onBlur={onBlur}
      className={
        className ??
        `mx-auto h-7 w-[80%] rounded-3xl border-0 px-4 text-black placeholder:text-sm focus:ring-2 ${focusClass} ${
          disabled ? 'cursor-not-allowed opacity-50' : ''
        }`
      }
      placeholder={placeholder}
      disabled={disabled}
      autoComplete={autoComplete}
    />
  )
}
