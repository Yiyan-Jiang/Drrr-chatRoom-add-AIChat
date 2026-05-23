/**
 * @parm 组件用途：展示主布局左侧导航栏。
 */
import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/home/news', label: '新闻流' },
  { path: '/home/rooms', label: '房间' },
  { path: '/home/board', label: '留言板' },
]

export default function LeftSidebar() {
  return (
    <div className="mx-auto mt-5 h-full w-[90%] space-y-3 bg-black lg:max-w-50">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `mx-auto block rounded-xl border-2 px-4 py-2 text-center transition-all ${
              isActive ? 'bg-[#666] font-bold text-white' : 'text-white hover:scale-105'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </div>
  )
}
