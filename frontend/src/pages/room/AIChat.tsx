import { useCallback, useEffect, useLayoutEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAIChat } from '@/hooks/useAIchat'
import { useChatScroll } from '@/hooks/useChatScroll'
import { useAuth } from '@/contexts/AuthContext'
import type { AICharacter } from '@/types/ai'
import type { Message } from '@/types/chat'
import ChatMessageViewport from '@/components/chat/ChatMessageViewport'
import ChatRoomHeader from '@/components/chat/ChatRoomHeader'
import { getUserDisplayName } from '@/utils/userDisplayName'

const CHARACTERS: { value: AICharacter; label: string; desc: string; avatarKey: string }[] = [
  { value: 'sakura', label: '小樱', desc: '傲娇系猫耳女仆', avatarKey: 'pink' },
  { value: 'rin', label: '凛', desc: '三无少女', avatarKey: 'gray' },
  { value: 'mio', label: '澪', desc: '病娇少女', avatarKey: 'zaika' },
  { value: 'yang', label: '葵', desc: '超级元气话痨少女', avatarKey: 'kanra' },
]

type AIChatLogItem = {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  sequence_no?: number
  created_at?: string
}

const ASSISTANT_USER_ID = 0
const DEFAULT_CHARACTER: AICharacter = 'sakura'

function normalizeCharacter(value: string | null): AICharacter {
  return CHARACTERS.some((char) => char.value === value) ? (value as AICharacter) : DEFAULT_CHARACTER
}

function getCharacterMeta(character: AICharacter) {
  return CHARACTERS.find((char) => char.value === character) ?? CHARACTERS[0]
}

function toMessage(
  item: AIChatLogItem,
  character: AICharacter,
  currentUser: { id: number; username: string; nickname?: string | null; avatar_key?: string | null },
): Message {
  const selectedCharacter = getCharacterMeta(character)

  return {
    id: item.id,
    content: item.content,
    user_id: item.role === 'system' ? null : item.role === 'assistant' ? ASSISTANT_USER_ID : currentUser.id,
    room_id: 0,
    message_type: item.role === 'system' ? 'system' : 'user',
    author: item.role === 'assistant'
      ? { id: ASSISTANT_USER_ID, username: selectedCharacter.label, avatar_key: selectedCharacter.avatarKey }
      : item.role === 'user'
        ? {
            id: currentUser.id,
            username: currentUser.username,
            nickname: currentUser.nickname,
            avatar_key: currentUser.avatar_key,
          }
        : null,
    created_at: item.created_at ?? new Date(item.id).toISOString(),
  }
}

export default function AIChat() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { containerRef, scrollToHead } = useChatScroll()
  const { user } = useAuth()

  const rawCharacter = searchParams.get('char')
  const character = normalizeCharacter(rawCharacter)

  const [input, setInput] = useState('')
  const [chatLog, setChatLog] = useState<AIChatLogItem[]>([])

  const {
    messages,
    historyItems,
    isLoading,
    error,
    sendMessage,
    clearHistory,
    abort,
    loadOlderHistory,
    hasMoreHistory,
    loadingOlderHistory,
  } = useAIChat({ character })

  const selectedCharacter = getCharacterMeta(character)
  const currentUser = useMemo(() => ({
    id: user?.id ?? 1,
    username: getUserDisplayName(user, '你'),
    nickname: user?.nickname,
    avatar_key: user?.avatar_key,
  }), [user])
  const historyLog = useMemo(() => historyItems.map((item) => ({
    id: item.id,
    role: item.role,
    content: item.content,
    sequence_no: item.sequence_no,
    created_at: item.created_at,
  })), [historyItems])
  const combinedLog = useMemo(() => [...chatLog, ...historyLog], [chatLog, historyLog])
  const renderedMessages = useMemo(
    () => combinedLog.map((item) => toMessage(item, character, currentUser)),
    [character, combinedLog, currentUser],
  )

  useEffect(() => {
    if (rawCharacter !== character) {
      setSearchParams({ char: character }, { replace: true })
    }
  }, [character, rawCharacter, setSearchParams])

  useEffect(() => {
    abort()
    setChatLog([])
    setInput('')
  }, [abort, character])

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setChatLog((prev) => [
      { id: Date.now(), role: 'user', content: userMessage },
      ...prev,
    ])

    try {
      await sendMessage(userMessage)
    } catch {
      // 错误已在 hook 中处理。
    }
  }, [input, isLoading, sendMessage])

  useEffect(() => {
    if (!error) return
    const timer = window.setTimeout(() => {
      setChatLog((prev) => [
        { id: Date.now(), role: 'system', content: error },
        ...prev,
      ])
    }, 0)
    return () => window.clearTimeout(timer)
  }, [error])

  useLayoutEffect(() => {
    if (!messages) return
    window.setTimeout(() => {
      setChatLog((prev) => {
        const head = prev[0]
        if (head?.role === 'assistant') {
          return [{ ...head, content: messages }, ...prev.slice(1)]
        }
        return [
          { id: Date.now(), role: 'assistant', content: messages },
          ...prev,
        ]
      })
      scrollToHead('auto')
    }, 0)
  }, [messages, scrollToHead])

  const handleClearHistory = useCallback(async () => {
    try {
      await clearHistory()
      setChatLog([])
      toast.success('对话已清空')
    } catch {
      toast.error('清空失败')
    }
  }, [clearHistory])

  const handleLeaveRoom = useCallback(() => {
    navigate('/home/rooms')
  }, [navigate])

  const handleScroll = useCallback(() => {
    const container = containerRef.current
    if (!container || loadingOlderHistory || !hasMoreHistory) return
    const distanceToTail = container.scrollHeight - container.scrollTop - container.clientHeight
    if (distanceToTail < 80) {
      void loadOlderHistory()
    }
  }, [containerRef, hasMoreHistory, loadOlderHistory, loadingOlderHistory])

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-black">
      <ChatRoomHeader
        roomName={`AI · ${selectedCharacter.label}`}
        roomId={0}
        subtitle={selectedCharacter.desc}
        composerValue={input}
        composerDisabled={isLoading}
        statusText={isLoading ? 'AI typing' : undefined}
        leaveLabel="退出"
        infoLabel="清空"
        onComposerChange={setInput}
        onSubmit={handleSend}
        onLeaveRoom={handleLeaveRoom}
        onOpenInfo={handleClearHistory}
      />

      <ChatMessageViewport
        messages={renderedMessages}
        currentUserId={currentUser.id}
        hasMore={hasMoreHistory}
        loadingOlder={loadingOlderHistory}
        unreadNewCount={0}
        containerRef={containerRef}
        onScroll={handleScroll}
        onJumpToHead={() => scrollToHead()}
      />
    </div>
  )
}
