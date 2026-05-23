/**
 * @parm 组件用途：展示房间搜索、排序和刷新工具栏。
 */
import type { ChangeEvent, FormEvent } from 'react'
import type { RoomSortKey } from '@/components/room/roomSort'

interface RoomFilterBarProps {
  sortKey: RoomSortKey
  searchInput: string
  onSortChange: (sortKey: RoomSortKey) => void
  onSearchInputChange: (value: string) => void
  onSearchSubmit: () => void
  onRefresh: () => void
}

const sortOptions: { value: RoomSortKey; label: string }[] = [
  { value: 'created_desc', label: '时间降序' },
  { value: 'created_asc', label: '时间升序' },
  { value: 'online_desc', label: '在线人数' },
  { value: 'max_members_desc', label: '最大人数' },
  { value: 'min_age_asc', label: '最小年龄' },
  { value: 'max_age_desc', label: '最大年龄' },
]

export default function RoomFilterBar({
  sortKey,
  searchInput,
  onSortChange,
  onSearchInputChange,
  onSearchSubmit,
  onRefresh,
}: RoomFilterBarProps) {
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    onSearchInputChange(event.target.value)
  }

  const handleSearchSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    onSearchSubmit()
  }

  const handleSortChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onSortChange(event.target.value as RoomSortKey)
  }

  return (
    <div className="flex justify-start gap-3">
      <form onSubmit={handleSearchSubmit}>
        <label>
          搜索：
          <input
            value={searchInput}
            onChange={handleSearchChange}
            placeholder="请输入房间名称"
            type="text"
            className="w-20 rounded-sm border border-white pl-2 outline-none placeholder:text-sm lg:w-40"
          />
        </label>
      </form>
      <label>
        排序：
        <select
          value={sortKey}
          onChange={handleSortChange}
          className="w-25 rounded-sm border border-white *:bg-[#090909] *:hover:bg-gray-400 lg:w-50"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <button onClick={onRefresh} className="rounded-md border border-white px-1 lg:w-20 lg:px-5 active:scale-95">
        更新
      </button>
    </div>
  )
}
