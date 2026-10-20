/** 提供进入独立 Markdown 发帖页的入口。 */
import { Link } from 'react-router-dom'

/** 提供进入独立 Markdown 发帖页的入口，并保留帖子列表中的加号样式。 */
export default function PostEditor() {
  return (
    <Link
      className="absolute bottom-4 right-4 z-20 flex h-12 w-12 items-center justify-center rounded-full border border-white bg-pink-100 text-2xl font-bold text-black shadow-lg transition hover:scale-105"
      to="/posts/new"
      aria-label="打开发帖页面"
    >
      +
    </Link>
  )
}
