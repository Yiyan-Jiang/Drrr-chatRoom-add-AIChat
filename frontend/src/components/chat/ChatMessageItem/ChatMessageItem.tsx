import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { Message } from '@/types/chat'
import { getUserDisplayName } from '@/utils/userDisplayName'
import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'

import './index.css'

interface ChatMessageItemProps {
  message: Message
  isOwn: boolean
}

export default function ChatMessageItem({ message, isOwn }: ChatMessageItemProps) {
  const author = message.author
  const assets = resolveChatAvatarAssets(author?.avatar_key)
  const displayName = isOwn ? '你' : getUserDisplayName(author, message.user_id ? `用户${message.user_id}` : '系统')
  const [profileOpen, setProfileOpen] = useState(false)
  const profileRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!profileOpen) return

    const onPointerDown = (event: PointerEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false)
      }
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setProfileOpen(false)
    }

    window.addEventListener('pointerdown', onPointerDown)
    window.addEventListener('keydown', onKeyDown)
    return () => {
      window.removeEventListener('pointerdown', onPointerDown)
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [profileOpen])

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[86%] gap-4 ${isOwn ? 'flex-row-reverse' : ''}`}>
        <div ref={profileRef} className="relative flex w-12 flex-none flex-col items-center gap-1">
          <button
            type="button"
            onClick={() => setProfileOpen((open) => !open)}
            className="block h-11 w-11 overflow-hidden rounded outline-none ring-offset-2 ring-offset-black transition hover:ring-2 hover:ring-zinc-500 focus-visible:ring-2 focus-visible:ring-cyan-400"
            aria-label="查看用户资料"
            aria-expanded={profileOpen}
          >
            <img src={assets.avatar} alt="" className="h-full w-full object-cover" loading="lazy" />
          </button>
          <div className="max-w-12 truncate text-center text-xs text-white">{displayName}</div>

          {profileOpen && (
            <div
              role="dialog"
              aria-label="用户资料"
              className={`absolute top-[calc(100%+0.5rem)] z-30 w-64 rounded-xl border border-zinc-800 bg-zinc-950 p-4 shadow-2xl shadow-black/60 ${
                isOwn ? 'right-0' : 'left-0'
              }`}
            >
              {author ? (
                <div className="flex items-start gap-3">
                  <img src={assets.avatar} alt="" className="h-14 w-14 shrink-0 rounded-lg object-cover" loading="lazy" />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-semibold text-zinc-100">{author.username}</div>
                    <div className="mt-0.5 truncate text-xs text-zinc-400">
                      {author.nickname?.trim() || '暂无昵称'}
                    </div>
                    <div className="mt-3 text-xs leading-relaxed text-zinc-300">
                      {author.bio?.trim() || '暂无简介'}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-zinc-400">用户信息不可用</div>
              )}
            </div>
          )}
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
