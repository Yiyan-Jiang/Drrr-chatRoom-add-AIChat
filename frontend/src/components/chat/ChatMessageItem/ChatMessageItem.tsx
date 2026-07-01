import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { Message } from '@/types/chat'
import type { CSSProperties } from 'react'
import UserHoverCard from '@/components/user/UserHoverCard'

import './index.css'

interface ChatMessageItemProps {
  message: Message
  isOwn: boolean
}

export default function ChatMessageItem({ message, isOwn }: ChatMessageItemProps) {
  const author = message.author
  const assets = resolveChatAvatarAssets(author?.avatar_key)

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[86%] gap-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
        <UserHoverCard
          user={author ?? null}
          align={isOwn ? 'right' : 'left'}
          avatarClassName="h-11 w-11"
          nameClassName="max-w-12 text-white"
        />

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
          <span className="chat-bubble__tail" aria-hidden="true">
            <span className="chat-bubble__tail-border" />
            <span className="chat-bubble__tail-fill" />
          </span>

          <div className="whitespace-pre-wrap wrap-break-word">{message.content}</div>
        </div>
      </div>
    </div>
  )
}
