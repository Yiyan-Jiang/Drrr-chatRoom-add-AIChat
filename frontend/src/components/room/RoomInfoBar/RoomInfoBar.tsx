/**
 * 展示房间列表顶部统计信息。
 */
interface RoomInfoBarProps {
  /** 调用方汇总的在线成员数量。 */
  totalOnlineMembers: number
}

/** 展示房间列表的在线人数汇总和固定提示。 */
export default function RoomInfoBar({ totalOnlineMembers }: RoomInfoBarProps) {
  return (
    <div className="mb-2 flex justify-between text-sm">
      <div>★ 现在总共 {totalOnlineMembers} 人在观看</div>
      <div>★ 与管理员的联系请通过公告板进行</div>
      <div className="hidden lg:block">★ 携带入口</div>
      <div className="hidden lg:block">★ 深圳</div>
    </div>
  )
}
