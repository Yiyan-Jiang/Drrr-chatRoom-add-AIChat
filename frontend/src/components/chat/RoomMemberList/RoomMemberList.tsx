/**
 * 展示房间在线成员列表。
 */
import type { RoomMember } from '@/types/chat'
import { getUserDisplayName } from '@/utils/userDisplayName'

/** 在线成员列表数据。 */
interface RoomMemberListProps {
  /** 按展示顺序提供的在线成员。 */
  members: RoomMember[]
}

/** 展示在线成员名称，列表为空时展示提示。 */
export default function RoomMemberList({ members }: RoomMemberListProps) {
  if (members.length === 0) {
    return <p className="text-sm text-zinc-500">暂无在线成员</p>
  }

  return (
    <ul className="space-y-2">
      {members.map((member) => (
        <li
          key={member.id}
          className="flex items-center gap-2 text-sm text-zinc-200"
        >
          <span className="grid h-5 w-5 place-items-center rounded bg-zinc-800 text-[10px]">
            M
          </span>
          <span>{getUserDisplayName(member)}</span>
        </li>
      ))}
    </ul>
  )
}
