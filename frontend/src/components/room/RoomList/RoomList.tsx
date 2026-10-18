/**
 * 展示房间列表、筛选栏和空状态。
 */
import type { Room } from '@/types/chat'
import RoomCard from '@/components/room/RoomCard'
import RoomFilterBar from '@/components/room/RoomFilterBar'
import RoomInfoBar from '@/components/room/RoomInfoBar'
import type { RoomSortKey } from '@/components/room/roomSort'

/** 房间列表的展示结果、筛选状态与操作回调。 */
interface RoomListProps {
  /** 已由调用方完成筛选与排序的房间。 */
  rooms: Room[]
  /** 是否展示加载状态并暂时隐藏列表。 */
  loading: boolean
  /** 当前排序选项。 */
  sortKey: RoomSortKey
  /** 搜索框中的当前文本。 */
  searchInput: string
  /** 房间列表顶部展示的在线成员汇总。 */
  totalOnlineMembers: number
  /** 请求更新房间排序方式。 */
  onSortChange: (sortKey: RoomSortKey) => void
  /** 接收编辑中的搜索文本。 */
  onSearchInputChange: (value: string) => void
  /** 提交当前搜索条件。 */
  onSearchSubmit: () => void
  /** 请求重新加载房间。 */
  onRefresh: () => void
}

/** 展示已筛选排序的房间、筛选工具栏与空状态，加载时仅展示加载提示。 */
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
