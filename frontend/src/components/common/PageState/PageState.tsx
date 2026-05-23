/**
 * @parm 组件用途：展示页面级 loading、error 或空状态。
 */
import type { ReactNode } from 'react'

interface PageStateProps {
  children: ReactNode
}

export default function PageState({ children }: PageStateProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <div className="text-gray-400">{children}</div>
    </div>
  )
}
