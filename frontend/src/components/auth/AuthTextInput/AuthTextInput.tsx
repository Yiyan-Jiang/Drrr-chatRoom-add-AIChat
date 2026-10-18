/**
 * 封装认证表单里复用的输入框。
 */
import type { ChangeEvent } from 'react'

/** 认证输入框的值、原生属性和焦点回调。 */
interface AuthTextInputProps {
  /** 原生输入元素 ID。 */
  id?: string
  /** 提交事件中用于识别字段的名称。 */
  name?: string
  /** 原生输入类型，默认 text。 */
  type?: string
  /** 父组件维护的输入值。 */
  value: string
  /** 输入为空时展示的提示。 */
  placeholder: string
  /** 是否禁用输入。 */
  disabled?: boolean
  /** 是否启用原生必填约束。 */
  required?: boolean
  /** 浏览器自动填充提示。 */
  autoComplete?: string
  /** 外部焦点状态；缺省时采用原生 focus 样式。 */
  focused?: boolean
  /** 覆盖默认输入框样式的完整类名。 */
  className?: string
  /** 接收原生输入变更事件。 */
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  /** 输入获得焦点时调用。 */
  onFocus?: () => void
  /** 输入失去焦点时调用。 */
  onBlur?: () => void
}

/** 渲染受控认证输入框；传入 className 时使用调用方提供的完整样式。 */
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
