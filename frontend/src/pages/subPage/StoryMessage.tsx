/** 使用真实聊天头像与气泡素材展示本地示例，不加载用户资料或业务连接。 */
import type { CSSProperties } from 'react'
import { chatAvatarCatalog } from '@/assets/chatAvatarCatalog'
import type { AvatarKey } from '@/types/user'
import '@/components/chat/ChatMessageItem/index.css'

/** 可在视觉叙事中重复使用的静态消息参数。 */
interface StoryMessageProps {
  /** 内置头像主题。 */
  avatar: AvatarKey
  /** 示例昵称。 */
  name: string
  /** 消息正文。 */
  children: string
  /** 反向排列头像与尾角。 */
  reverse?: boolean
}

/** 保持真实聊天气泡的纹理与尾角，供介绍页编排示例对话。 */
export default function StoryMessage({
  avatar,
  name,
  children,
  reverse = false,
}: StoryMessageProps) {
  const assets = chatAvatarCatalog[avatar]
  return (
    <div className={`story-message${reverse ? ' story-message--reverse' : ''}`}>
      <div className="story-message-person">
        <img src={assets.avatar} alt="" width="48" height="48" />
        <span>{name}</span>
      </div>
      <div
        className={`chat-bubble ${reverse ? 'chat-bubble--right' : 'chat-bubble--left'} story-message-bubble`}
        style={
          {
            '--bubble-image': `url(${assets.bubble})`,
            backgroundImage: `url(${assets.bubble})`,
          } as CSSProperties
        }
      >
        <span className="chat-bubble__tail" aria-hidden="true">
          <span className="chat-bubble__tail-border" />
          <span className="chat-bubble__tail-fill" />
        </span>
        {children}
      </div>
    </div>
  )
}
