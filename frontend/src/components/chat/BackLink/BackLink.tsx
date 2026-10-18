/**
 * 展示聊天页面顶部的返回链接。
 */
import { Link } from 'react-router-dom'

/** 返回链接的路由配置。 */
interface BackLinkProps {
  /** 点击返回图标时前往的路由。 */
  to: string
}

/** 渲染指向指定路由的返回图标链接。 */
export default function BackLink({ to }: BackLinkProps) {
  return (
    <Link
      to={to}
      className="rounded-lg bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white"
    >
      <svg
        className="h-5 w-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 19l-7-7m0 0l7-7m-7 7h18"
        />
      </svg>
    </Link>
  )
}
