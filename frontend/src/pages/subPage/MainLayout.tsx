/** 组合主导航与子路由；设定页使用独立的全屏叙事布局。 */
import { Outlet, useLocation } from 'react-router-dom'
import AppHeader from '@/components/layout/AppHeader'

/** 仅为设定页让出完整视口，其余页面沿用公共页头与内容宽度。 */
export default function MainLayout() {
  const { pathname } = useLocation()
  if (pathname === '/settings' || pathname === '/settings/') return <Outlet />

  return (
    <div className="mx-auto flex h-screen w-full flex-col overflow-hidden bg-black lg:max-w-[80%]">
      <AppHeader />
      <Outlet />
    </div>
  )
}
