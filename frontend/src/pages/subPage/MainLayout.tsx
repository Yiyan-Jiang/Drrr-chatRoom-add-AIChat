import { Outlet } from 'react-router-dom'
import AppHeader from '@/components/layout/AppHeader'

export default function MainLayout() {
  return (
    <div className="mx-auto flex h-screen w-full flex-col overflow-hidden bg-black lg:max-w-[80%]">
      <AppHeader />
      <Outlet />
    </div>
  )
}
