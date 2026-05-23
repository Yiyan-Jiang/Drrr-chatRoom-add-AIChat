/**
 * @parm 组件用途：展示带头像和气泡样式的单条聊天室消息。
 */
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { CSSProperties } from 'react'
import type { Message } from '@/types/chat'

import './index.css'

interface ChatMessageItemProps {
  message: Message
  isOwn: boolean
}

// function formatTime(value: string) {
//   return new Date(value).toLocaleTimeString('zh-CN', {
//     hour: '2-digit',
//     minute: '2-digit',
//     hour12: false,
//   })
// }

export default function ChatMessageItem({ message, isOwn }: ChatMessageItemProps) {
  const author = message.author
  const assets = resolveChatAvatarAssets(author?.avatar_key)
  const displayName = isOwn ? '你' : author?.username || (message.user_id ? `用户${message.user_id}` : '系统')

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[86%] gap-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
        <div className="flex w-12 flex-none flex-col items-center gap-1">

          {/* 头像 */}
          <img
            src={assets.avatar}
            alt=""
            className="h-11 w-11 rounded object-cover"
            loading="lazy"
          />
          <div className="max-w-12 truncate text-center text-xs text-white">{displayName}</div>
        </div>

        <div
          className={[
            'chat-bubble',
            isOwn ? 'chat-bubble--right' : 'chat-bubble--left',
            'rounded-xl border-3 px-4 py-3 leading-relaxed text-white text-lg shadow',
          ].join(' ')}
          style={{
            '--bubble-image': `url(${assets.bubble})`,
            backgroundImage: `url(${assets.bubble})`,
            backgroundSize: 'contain',
          } as CSSProperties}
        >

          {/* 气泡尖角 */}
          <span className="chat-bubble__tail" aria-hidden="true">
            <span className="chat-bubble__tail-border" />
            <span className="chat-bubble__tail-fill" />
          </span>

          {/* 内容部分 */}
          <div className="whitespace-pre-wrap wrap-break-word">{message.content}</div>

          {/* 后面这里是发送的时间，考虑一下要不要，感觉观感不是很好 */}
          {/* <div className="mt-1 text-right text-[11px] text-zinc-700">
            {message.delivery_status === 'sending' ? 'sending ' : null}
            {message.delivery_status === 'failed' ? 'failed ' : null}
            {formatTime(message.created_at)}
          </div> */}
        </div>
      </div>
    </div>
  )
}
