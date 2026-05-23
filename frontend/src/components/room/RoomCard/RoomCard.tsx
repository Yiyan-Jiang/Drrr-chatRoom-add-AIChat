/**
 * @parm 组件用途：展示单个聊天室卡片和进入入口。
 */
import { Link } from 'react-router-dom'
import type { Room } from '@/types/chat'
import { formatAgeRange, formatCreatedAt } from '@/components/room/roomFormatters'

interface RoomCardProps {
  room: Room
}

function ChatBubbleIcon() {
  return (
    <svg
      className="h-16 w-16 text-white transition-transform group-hover:scale-105"
      viewBox="0 0 64 64"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 28.5C12 18.84 20.73 11 31.5 11S51 18.84 51 28.5 42.27 46 31.5 46a22.9 22.9 0 0 1-6.23-.85L14.5 51l2.53-10.04A16.58 16.58 0 0 1 12 28.5Z" />
      <path d="M22 25h19" />
      <path d="M22 32h15" />
      <path d="M22 39h8" />
      <path d="M46 42.5c4.03 1.93 6.5 5.44 6.5 9.18 0 1.53-.41 3-1.17 4.33L53 62l-6.02-3.25a16.1 16.1 0 0 1-4.48.63c-5.8 0-10.77-2.89-12.81-7.01" />
      <path d="M39 51h6" />
    </svg>
  )
}

function UsersIcon() {
  return (
    <svg
      className="h-4 w-4 opacity-90"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  )
}

export default function RoomCard({ room }: RoomCardProps) {
  const onlineMembers = room.online_members ?? 0

  return (
    <Link
      to={`/chat/${room.id}`}
      className="group flex justify-between rounded-xl border border-white-2 p-5 text-[#f5f5f5] transition-all hover:bg-[#666]"
    >
      <div className="flex w-15 shrink-0 items-center justify-center lg:w-25">
        <ChatBubbleIcon />
      </div>

      <div className="flex flex-4 items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="truncate font-semibold text-white">{room.name}</h3>

          <p className="mt-2 line-clamp-2 text-sm text-gray-300">{room.description || '暂无简介'}</p>

          <div className="mt-4 flex min-h-7 items-center justify-center gap-3 text-sm text-white">
            {room.tags.length > 0 ? room.tags.map((tag) => <span key={tag}>{tag}</span>) : <span>无标签</span>}

            <div className="max-h-3 border-l-2 border-white text-transparent">1</div>

            <div className="flex items-center justify-between gap-3">
              <div>{formatAgeRange(room)}</div>
            </div>

            <div className="max-h-3 border-l-2 border-white text-transparent">1</div>

            <div className="hidden items-center justify-between gap-3 lg:flex">
              <div>{formatCreatedAt(room.created_at)}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex w-30 flex-col items-center justify-center gap-1">
        <div className="flex items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-1.5">
            <UsersIcon />
            <span>{onlineMembers} / {room.max_members}</span>
          </div>
        </div>
        <div className="h-7 w-[90%] rounded-md border border-white bg-black text-center leading-7 transition group-hover:scale-105">
          进入
        </div>
      </div>
    </Link>
  )
}
