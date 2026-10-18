/** 房间主页的侧栏与子路由布局。 */
import { Outlet } from 'react-router-dom'
import LeftSidebar from '@/components/layout/LeftSidebar'
import RightSidebar from '@/components/layout/RightSidebar'

/** 组合左右侧栏与中间子路由内容的房间主页布局。 */
export default function RoomList() {
  return (
    <div className="mx-auto min-h-0 w-full flex-1 overflow-hidden bg-black lg:max-w-full">
      <div className="flex h-full min-h-0 w-full justify-between">
        <div className="h-full flex-2 overflow-hidden">
          <LeftSidebar />
        </div>
        <div className="min-h-0 flex-5 overflow-hidden lg:flex-7">
          <Outlet />
        </div>
        <div className="h-full flex-3 overflow-auto">
          <RightSidebar />
        </div>
      </div>
    </div>
  )
}
