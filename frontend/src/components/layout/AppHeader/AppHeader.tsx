/**
 * @parm 组件用途：展示主布局顶部品牌、导航和在线人数。
 */
import { NavLink } from 'react-router-dom'
import logoUrl from '@/assets/icon/Logo/logo.png'
import { useUserCount } from '@/hooks/useUserCount'
import AppNav from '@/components/layout/AppNav'

const NAV_ITEMS = [
  { path: '/home', label: '主页' },
  { path: '/my', label: '我的页面' },
  { path: '/friends', label: '友达' },
  { path: '/mailbox', label: '邮箱' },
  { path: '/profile', label: '个人资料' },
  { path: '/settings', label: '设定' },
  { path: '/help', label: '帮助' },
]

export default function AppHeader() {
  const { data } = useUserCount()

  return (
    <div className="h-57 w-full shrink-0 border-y-5 border-[#EAEAEB] pb-3">
      <div className="mt-2 h-2 bg-[#EAEAEB]" />
      <div className="flex h-[95%] w-full border-b border-[#EAEAEB] p-3">
        <div className="ml-10 h-full w-50 text-center">
          <img src={logoUrl} alt="Logo" className="h-45 w-45" />
        </div>

        <div className="flex w-full flex-1 flex-col justify-between">
          <div className="w-full">
            <AppNav />
          </div>

          <div className="flex w-full items-end justify-around">
            <div className="flex items-end">
              当前成员:
              <span className="ml-2 block h-8 w-4 rounded-l-2xl border-2 border-[#666] text-transparent" />
              {String(data?.total ?? '')
                .padStart(4, '0')
                .split('')
                .map((num, index) => (
                  <span key={index} className="border border-y-2 border-[#666] p-0.5">
                    {num}
                  </span>
                ))}
              <span className="mr-2 block h-8 w-4 rounded-r-2xl border-2 border-[#666] text-transparent" />
              名
            </div>

            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  isActive ? 'font-bold text-white underline' : 'transition-colors hover:text-gray-300'
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
