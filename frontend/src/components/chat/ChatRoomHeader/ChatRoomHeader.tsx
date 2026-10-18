/**
 * 普通聊天与私聊共用的标题、状态和输入栏。
 */
import ChatComposer from '@/components/chat/ChatComposer'

/** 聊天页标题、消息输入和房间操作配置。 */
interface ChatRoomHeaderProps {
  /** 标题中展示的房间或会话名称。 */
  roomName: string
  /** 默认副标题使用的房间编号。 */
  roomId: number
  /** 父组件维护的消息草稿。 */
  composerValue: string
  /** 未提供状态文案时显示重连提示。 */
  reconnecting?: boolean
  /** 禁用消息输入与发送。 */
  composerDisabled?: boolean
  /** 资料按钮文字及无障碍名称，默认“简介”。 */
  infoLabel?: string
  /** 离开按钮文字，默认“退出”。 */
  leaveLabel?: string
  /** 优先展示的连接状态文案。 */
  statusText?: string
  /** 覆盖默认房间编号的副标题。 */
  subtitle?: string
  /** 接收新的消息草稿。 */
  onComposerChange: (value: string) => void
  /** 提交当前消息草稿。 */
  onSubmit: () => void
  /** 处理离开当前会话的操作。 */
  onLeaveRoom: () => void
  /** 打开房间或会话资料。 */
  onOpenInfo: () => void
}

/** 组合房间标题、状态、操作按钮与消息输入区。 */
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
            <h1 className="truncate text-sm font-semibold text-zinc-100">
              {roomName}
            </h1>
            <p className="text-xs text-zinc-500">
              {subtitle ?? `room #${roomId}`}
            </p>
          </div>
          {statusText || reconnecting ? (
            <span className="text-xs text-amber-300">
              {statusText ?? 'reconnecting'}
            </span>
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
