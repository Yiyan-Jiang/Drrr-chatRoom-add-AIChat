/**
 * @parm 组件用途：展示房间在线成员列表。
 */
import type { RoomMember } from '@/types/chat'

interface RoomMemberListProps {
  members: RoomMember[]
}

export default function RoomMemberList({ members }: RoomMemberListProps) {
  if (members.length === 0) {
    return <p className="text-sm text-zinc-500">暂无在线成员</p>
  }

  return (
    <ul className="space-y-2">
      {members.map((member) => (
        <li key={member.id} className="flex items-center gap-2 text-sm text-zinc-200">
          <span className="grid h-5 w-5 place-items-center rounded bg-zinc-800 text-[10px]">M</span>
          <span>{member.username}</span>
        </li>
      ))}
    </ul>
  )
}
