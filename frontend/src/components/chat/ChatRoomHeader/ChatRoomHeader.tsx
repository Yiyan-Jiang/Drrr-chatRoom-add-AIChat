/**
 * @parm 组件用途：展示普通聊天室顶部房间信息和输入栏。
 */
import ChatComposer from '@/components/chat/ChatComposer'

interface ChatRoomHeaderProps {
  roomName: string
  roomId: number
  composerValue: string
  reconnecting?: boolean
  composerDisabled?: boolean
  infoLabel?: string
  leaveLabel?: string
  statusText?: string
  subtitle?: string
  onComposerChange: (value: string) => void
  onSubmit: () => void
  onLeaveRoom: () => void
  onOpenInfo: () => void
}

export default function ChatRoomHeader({
  roomName,
  roomId,
  composerValue,
  reconnecting,
  composerDisabled,
  infoLabel = '简介',
  leaveLabel = '退出',
  statusText,
  subtitle,
  onComposerChange,
  onSubmit,
  onLeaveRoom,
  onOpenInfo,
}: ChatRoomHeaderProps) {
  return (
    <header className="border-b border-zinc-800 bg-[#39393E] px-4 py-3">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-30">
        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onLeaveRoom}
            className="h-8 rounded border border-[#4D4D4D] px-3 text-xs text-zinc-200 hover:border-white"
          >
            {leaveLabel}
          </button>
          <button
            type="button"
            onClick={onOpenInfo}
            className="h-8 rounded border border-[#4D4D4D] px-3 text-xs text-zinc-200 hover:border-white"
            aria-label={infoLabel}
          >
            {infoLabel}
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-sm font-semibold text-zinc-100">{roomName}</h1>
            <p className="text-xs text-zinc-500">{subtitle ?? `room #${roomId}`}</p>
          </div>
          {statusText || reconnecting ? (
            <span className="text-xs text-amber-300">{statusText ?? 'reconnecting'}</span>
          ) : null}
        </div>

        <ChatComposer
          value={composerValue}
          disabled={composerDisabled ?? reconnecting}
          onChange={onComposerChange}
          onSubmit={onSubmit}
        />
      </div>
    </header>
  )
}
