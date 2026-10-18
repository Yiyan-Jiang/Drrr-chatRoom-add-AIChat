/** 组合主导航头部与子路由内容。 */
import { Outlet } from 'react-router-dom'
import AppHeader from '@/components/layout/AppHeader'

/** 组合主导航头部与子路由内容。 */
export default function MainLayout() {
  return (
    <div className="mx-auto flex h-screen w-full flex-col overflow-hidden bg-black lg:max-w-[80%]">
      <AppHeader />
      <Outlet />
    </div>
  )
}
