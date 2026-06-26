/**
 * @parm 组件用途：展示当前用户创建的房间列表和空状态入口。
 */
import { Link } from 'react-router-dom'
import type { Room } from '@/types/chat'
import { formatProfileDate } from './profilePageModel'

type OwnedRoomsSectionProps = {
  rooms: Room[]
}

export function OwnedRoomsSection({ rooms }: OwnedRoomsSectionProps) {
  return (
    <section className="mt-4 rounded-sm border border-zinc-700 bg-black/80">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
        <h2 className="text-sm font-semibold tracking-normal text-white">最近发布</h2>
        <Link to="/home/rooms" className="text-xs text-zinc-400 transition hover:text-white">
          查看更多 〉
        </Link>
      </div>

      {rooms.length === 0 ? (
        <div className="flex flex-col items-center gap-3 px-6 py-12 text-center">
          <p className="text-sm font-medium text-zinc-300">还没有创建房间</p>
          <p className="max-w-sm text-xs leading-relaxed text-zinc-500">
            创建一个安静的房间，等待想聊天的人加入。
          </p>
          <Link
            to="/home/rooms"
            className="mt-1 inline-flex h-9 items-center rounded-sm border border-zinc-500 px-5 text-sm font-semibold text-zinc-100 transition hover:bg-zinc-100 hover:text-black"
          >
            创建房间
          </Link>
        </div>
      ) : (
        <div className="divide-y divide-zinc-900">
          {rooms.map((room) => (
            <Link
              key={room.id}
              to={`/chat/${room.id}`}
              className="grid gap-4 px-3 py-3 transition hover:bg-zinc-950 sm:grid-cols-[128px_minmax(0,1fr)_180px]"
            >
              <div className="aspect-[16/9] rounded-sm border border-zinc-800 bg-[radial-gradient(circle_at_30%_30%,#3f3f46,#09090b_55%,#000)] grayscale" />
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-sm border border-zinc-600 px-2 py-0.5 text-xs text-zinc-300">
                    {room.tags[0] || '闲聊'}
                  </span>
                  <h3 className="truncate text-base font-semibold text-zinc-100">{room.name}</h3>
                </div>
                <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-zinc-400">
                  {room.description || '夜猫子集合，慢慢聊。'}
                </p>
              </div>
              <div className="flex items-center justify-start gap-5 font-mono text-xs tabular-nums text-zinc-400 sm:justify-end">
                <span>COM {room.online_members ?? 0}</span>
                <span>LIKE {room.peak_online_members}</span>
                <span>{formatProfileDate(room.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  )
}
