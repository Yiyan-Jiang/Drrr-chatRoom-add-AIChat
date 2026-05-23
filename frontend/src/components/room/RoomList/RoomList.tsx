/**
 * @parm 组件用途：展示房间列表、筛选栏和空状态。
 */
import type { Room } from '@/types/chat'
import RoomCard from '@/components/room/RoomCard'
import RoomFilterBar from '@/components/room/RoomFilterBar'
import RoomInfoBar from '@/components/room/RoomInfoBar'
import type { RoomSortKey } from '@/components/room/roomSort'

interface RoomListProps {
  rooms: Room[]
  loading: boolean
  sortKey: RoomSortKey
  searchInput: string
  totalOnlineMembers: number
  onSortChange: (sortKey: RoomSortKey) => void
  onSearchInputChange: (value: string) => void
  onSearchSubmit: () => void
  onRefresh: () => void
}

export default function RoomList({
  rooms,
  loading,
  sortKey,
  searchInput,
  totalOnlineMembers,
  onSortChange,
  onSearchInputChange,
  onSearchSubmit,
  onRefresh,
}: RoomListProps) {
  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-gray-400">加载中...</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <RoomInfoBar totalOnlineMembers={totalOnlineMembers} />
      <RoomFilterBar
        sortKey={sortKey}
        searchInput={searchInput}
        onSortChange={onSortChange}
        onSearchInputChange={onSearchInputChange}
        onSearchSubmit={onSearchSubmit}
        onRefresh={onRefresh}
      />
      {rooms.length === 0 ? (
        <div className="flex h-64 flex-col items-center justify-center text-gray-400">
          <p className="mb-2">还没有匹配的房间</p>
          <p className="text-sm">可以调整搜索词，或创建第一个房间</p>
        </div>
      ) : (
        rooms.map((room) => <RoomCard key={room.id} room={room} />)
      )}
    </div>
  )
}
