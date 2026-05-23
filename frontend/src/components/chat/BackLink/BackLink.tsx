/**
 * @parm 组件用途：展示聊天页面顶部的返回链接。
 */
import { Link } from 'react-router-dom'

interface BackLinkProps {
  to: string
}

export default function BackLink({ to }: BackLinkProps) {
  return (
    <Link to={to} className="rounded-lg bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white">
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </Link>
  )
}
