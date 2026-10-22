/** 房间主页的侧栏与子路由布局。 */
import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import LeftSidebar from '@/components/layout/LeftSidebar'
import RightSidebar from '@/components/layout/RightSidebar'

/** 组合左右侧栏与中间子路由内容的房间主页布局。 */
export default function RoomList() {
  const [friendsCollapsed, setFriendsCollapsed] = useState(false)

  return (
    <div className="mx-auto min-h-0 w-full flex-1 overflow-hidden bg-black lg:max-w-full">
      <div className="flex h-full min-h-0 w-full justify-between">
        <div className="h-full flex-2 overflow-hidden">
          <LeftSidebar />
        </div>
        <div className="min-h-0 min-w-0 flex-5 overflow-hidden lg:flex-7">
          <Outlet />
        </div>
        <div
          className={`relative h-[80%] min-w-0 ${friendsCollapsed ? 'w-0 shrink-0' : 'flex-3'}`}
        >
          <div
            id="home-friends-panel"
            hidden={friendsCollapsed}
            className="h-full"
          >
            <RightSidebar />
          </div>
          <button
            type="button"
            aria-label={friendsCollapsed ? '展开好友栏' : '收起好友栏'}
            aria-expanded={!friendsCollapsed}
            aria-controls="home-friends-panel"
            title={friendsCollapsed ? '展开好友栏' : '收起好友栏'}
            onClick={() => setFriendsCollapsed((collapsed) => !collapsed)}
            className={`absolute top-1/2 z-10 flex h-8 w-6 -translate-y-1/2 items-center justify-center border border-white bg-[#0D0D0D] text-white hover:bg-zinc-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white ${friendsCollapsed ? 'right-1' : 'left-1 -translate-x-1/2'}`}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-4 w-4"
              aria-hidden="true"
            >
              <path d={friendsCollapsed ? 'm14 6-6 6 6 6' : 'm10 6 6 6-6 6'} />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
