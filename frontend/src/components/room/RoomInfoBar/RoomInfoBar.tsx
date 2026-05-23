/**
 * @parm 组件用途：展示房间列表顶部统计信息。
 */
interface RoomInfoBarProps {
  totalOnlineMembers: number
}

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
