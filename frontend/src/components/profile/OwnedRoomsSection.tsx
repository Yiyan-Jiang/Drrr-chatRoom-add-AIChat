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
    <section className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold tracking-tight">我创建的房间</h2>
        <span className="font-mono text-sm tabular-nums text-zinc-500">{rooms.length} 个</span>
      </div>

      {rooms.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-zinc-800 px-6 py-12 text-center">
          <p className="text-sm font-medium text-zinc-300">还没有创建房间</p>
          <p className="max-w-sm text-xs leading-relaxed text-zinc-500">
            创建一个属于你的聊天室，邀请大家一起聊天、分享与讨论。
          </p>
          <Link
            to="/home/rooms"
            className="mt-1 inline-flex h-9 items-center rounded-lg bg-zinc-100 px-5 text-sm font-semibold text-black transition active:scale-[0.98]"
          >
            去创建房间
          </Link>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {rooms.map((room) => (
            <Link
              key={room.id}
              to={`/chat/${room.id}`}
              className="group flex flex-col rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 transition hover:border-zinc-600 hover:bg-zinc-900/40"
            >
              <div className="truncate text-sm font-semibold text-zinc-100">{room.name}</div>
              <div className="mt-1 line-clamp-2 text-xs leading-relaxed text-zinc-500">
                {room.description || '暂无简介'}
              </div>

              {room.tags.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5">
                  {room.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-zinc-800 bg-zinc-900/60 px-2 py-0.5 text-[10px] text-zinc-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-3 flex items-center justify-between font-mono text-xs tabular-nums text-zinc-500">
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500/70" />
                  {room.online_members ?? 0} / {room.max_members}
                </span>
                <span className="text-zinc-600">峰值 {room.peak_online_members}</span>
              </div>
              <div className="mt-1.5 text-[11px] text-zinc-600">{formatProfileDate(room.created_at)} 创建</div>
            </Link>
          ))}
        </div>
      )}
    </section>
  )
}
