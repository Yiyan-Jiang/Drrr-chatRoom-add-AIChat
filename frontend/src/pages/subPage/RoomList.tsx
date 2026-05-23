import { Outlet } from 'react-router-dom';
import LeftSidebar from '@/components/layout/LeftSidebar'
import RightSidebar from '@/components/layout/RightSidebar'

export default function RoomList() {
  return (
    <div className="mx-auto min-h-0 w-full flex-1 overflow-hidden bg-black lg:max-w-full">
      <div className='flex h-full min-h-0 w-full justify-between'>
        <div className='h-full flex-2 overflow-hidden'>
          <LeftSidebar />
        </div>
        <div className='min-h-0 flex-5 overflow-hidden lg:flex-7'>
          <Outlet />
        </div>
        <div className='h-full flex-3 overflow-auto'>
          <RightSidebar />
        </div>
      </div>
    </div>
  )
}
