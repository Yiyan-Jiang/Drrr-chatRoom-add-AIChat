/**
 * 展示页面级 loading、error 或空状态。
 */
import type { ReactNode } from 'react'

/** 页面状态容器的内容。 */
interface PageStateProps {
  /** 调用方提供的加载、错误或其他状态节点。 */
  children: ReactNode
}

/** 将调用方提供的状态内容放入全屏居中容器。 */
export default function PageState({ children }: PageStateProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <div className="text-gray-400">{children}</div>
    </div>
  )
}
