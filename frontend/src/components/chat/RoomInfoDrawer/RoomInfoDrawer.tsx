import { useEffect, useMemo, useState, type ReactNode } from 'react'
import toast from 'react-hot-toast'
import { images } from '@/assets/assets'
import type { RoomWithMessages, UpdateRoomRequest } from '@/types/chat'
import { getUserDisplayName } from '@/utils/userDisplayName'

type RoomInfoForm = Required<UpdateRoomRequest>

interface RoomInfoDrawerProps {
  open: boolean
  room: RoomWithMessages
  currentUserId?: number
  deletingRoom?: boolean
  updatingRoom?: boolean
  onClose: () => void
  onDeleteRoom: () => Promise<void> | void
  onUpdateRoom: (data: RoomInfoForm) => Promise<void>
}

const roomNamePattern = /^[\u4e00-\u9fa5A-Za-z0-9_]{1,8}$/

function toForm(room: RoomWithMessages): RoomInfoForm {
  return {
    name: room.name ?? '',
    description: room.description ?? '',
    notice: room.notice ?? '',
    rules: room.rules ?? '',
  }
}

function normalizeForm(form: RoomInfoForm): RoomInfoForm {
  return {
    name: form.name.trim(),
    description: form.description.trim(),
    notice: form.notice,
    rules: form.rules,
  }
}

function formatRoomDate(value: string) {
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatRoomId(id: number) {
  return String(id).padStart(3, '0')
}

function Section({
  title,
  icon,
  children,
  className = '',
}: {
  title: string
  icon?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <section className={`rounded-lg border border-white/10 bg-white/[0.03] ${className}`}>
      <div className="flex items-center gap-2 border-b border-white/5 px-4 py-3">
        {icon ? <span className="text-zinc-300">{icon}</span> : null}
        <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
      </div>
      <div className="px-4 py-4 text-sm leading-6 text-zinc-200">{children}</div>
    </section>
  )
}

function StatItem({
  icon,
  label,
  value,
}: {
  icon: ReactNode
  label: string
  value: ReactNode
}) {
  return (
    <div className="flex items-center gap-3 px-4 py-4">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-white/10 bg-black/40 text-zinc-100">
        {icon}
      </div>
      <div className="min-w-0">
        <div className="text-xs text-zinc-400">{label}</div>
        <div className="truncate text-lg font-semibold text-zinc-100">{value}</div>
      </div>
    </div>
  )
}

function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-md border border-white/15 bg-black/35 px-3 py-1 text-xs text-zinc-100">
      {children}
    </span>
  )
}

function BubbleIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M12 20c5 0 9-3.58 9-8s-4-8-9-8-9 3.58-9 8c0 2.04.87 3.9 2.32 5.31-.31 1.03-.85 2.19-1.63 3.46 2.08-.08 3.79-.56 5.11-1.41 1.02.4 2.16.64 3.2.64Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M9 11.8h.01M12 11.8h.01M15 11.8h.01" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  )
}

function UserIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M20 21a8 8 0 10-16 0"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <path
        d="M12 12a4 4 0 100-8 4 4 0 000 8Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function TrendIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M4 17l6-6 4 4 6-8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M14 7h6v6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function ChartIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M4 19h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M7 19V10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M12 19V5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M17 19v-8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

function ClockIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.6" />
      <path d="M12 8v4l3 2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function TagIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M4 11.5V6.8c0-.44.17-.86.48-1.17l1.15-1.15c.31-.31.73-.48 1.17-.48H11l6.8 6.8c.8.8.8 2.09 0 2.89l-5.4 5.4c-.8.8-2.09.8-2.89 0L4 11.5Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <circle cx="8.5" cy="8.5" r="1" fill="currentColor" />
    </svg>
  )
}

function ShieldIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M12 3 5 6v5c0 4.9 3.15 8.96 7 10 3.85-1.04 7-5.1 7-10V6l-7-3Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M9.5 12.2l1.8 1.8 3.8-4.1" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function PencilIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M4 16.5V20h3.5L18.4 9.1a1.8 1.8 0 0 0 0-2.6l-.9-.9a1.8 1.8 0 0 0-2.6 0L4 16.5Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M13.2 6.8 17.2 10.8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

function TrashIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M5 7h14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M9 7V5.8c0-.99.8-1.8 1.8-1.8h2.4c1 0 1.8.81 1.8 1.8V7" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 7l.7 12h6.6L16 7" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  )
}

function XIcon({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M6 6l12 12M18 6 6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

export default function RoomInfoDrawer({
  open,
  room,
  currentUserId,
  deletingRoom,
  updatingRoom,
  onClose,
  onDeleteRoom,
  onUpdateRoom,
}: RoomInfoDrawerProps) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<RoomInfoForm>(() => toForm(room))

  const normalizedForm = useMemo(() => normalizeForm(form), [form])
  const hasChanges =
    normalizedForm.name !== room.name ||
    normalizedForm.description !== (room.description ?? '') ||
    normalizedForm.notice !== (room.notice ?? '') ||
    normalizedForm.rules !== (room.rules ?? '')

  const isOwner = room.owner_id === currentUserId
  const ownerName = room.owner?.username || (room.owner_id ? `user${room.owner_id}` : '未知')
  const displayOwnerName = getUserDisplayName(room.owner, ownerName)
  const roomTags = room.tags.length > 0 ? room.tags : ['杂谈']
  const currentTitle = editing ? normalizedForm.name || '未命名房间' : room.name

  useEffect(() => {
    if (!open) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      if (editing && hasChanges && !window.confirm('有未保存的修改，确认放弃吗？')) return
      setEditing(false)
      onClose()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [editing, hasChanges, onClose, open])

  useEffect(() => {
    if (!open) return
    setEditing(false)
    setForm(toForm(room))
  }, [open, room])

  if (!open) return null

  const handleClose = () => {
    if (deletingRoom) return
    if (editing && hasChanges && !window.confirm('有未保存的修改，确认放弃吗？')) return
    setEditing(false)
    onClose()
  }

  const handleCancel = () => {
    setForm(toForm(room))
    setEditing(false)
  }

  const handleSave = async () => {
    if (!roomNamePattern.test(normalizedForm.name)) {
      toast.error('房间名只能包含中文、英文、数字和下划线，长度 1 到 8 个字符')
      return
    }
    if (!hasChanges) {
      setEditing(false)
      return
    }

    setEditing(false)
    try {
      await onUpdateRoom(normalizedForm)
    } catch (error) {
      setForm(toForm(room))
      setEditing(true)
      const message = error instanceof Error ? error.message : '更新房间信息失败'
      window.alert(message)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('确认删除这个房间吗？删除后无法恢复。')) return
    try {
      await onDeleteRoom()
    } catch (error) {
      const message = error instanceof Error ? error.message : '删除房间失败'
      window.alert(message)
    }
  }

  const beginEdit = () => {
    setForm(toForm(room))
    setEditing(true)
  }

  return (
    <div className="fixed inset-0 z-40 bg-black/75 px-4 py-6 backdrop-blur-sm" onClick={handleClose}>
      <section
        role="dialog"
        aria-modal="true"
        aria-label="房间简介"
        className="mx-auto flex max-h-[calc(100vh-3rem)] w-full max-w-5xl flex-col overflow-hidden border border-white/10 bg-[#070707] text-white shadow-[0_30px_90px_rgba(0,0,0,0.65)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="relative flex items-center justify-center border-b border-white/10 px-5 py-4">
          <div className="text-lg font-medium tracking-wide text-zinc-100">房间介绍</div>
          <button
            type="button"
            disabled={deletingRoom}
            onClick={handleClose}
            className="absolute right-4 top-1/2 grid h-10 w-10 -translate-y-1/2 place-items-center text-zinc-200 transition hover:text-white disabled:cursor-not-allowed disabled:text-zinc-600"
            aria-label="关闭"
          >
            <XIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4 sm:px-5">
          <div className="grid gap-5 lg:grid-cols-[320px_minmax(0,1fr)]">
            <div className="overflow-hidden border border-white/10 bg-[#101010] p-3">
              <div
                className="relative aspect-[4/3] overflow-hidden border border-white/10 bg-[#0d0d0d]"
                style={{
                  backgroundImage: [
                    'radial-gradient(circle at 50% 18%, rgba(255,255,255,0.12), transparent 22%)',
                    'linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 55%, rgba(0,0,0,0.28) 100%)',
                    'repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0 2px, transparent 2px 15px)',
                    'repeating-linear-gradient(0deg, rgba(255,255,255,0.03) 0 1px, transparent 1px 18px)',
                  ].join(', '),
                }}
              >
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,transparent_48%,rgba(0,0,0,0.3)_100%)]" />
                <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/70 to-transparent" />
                <div className="absolute inset-0 flex flex-col justify-between p-4">
                  <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.28em] text-white/55">
                    <span>room</span>
                    <span>{roomTags[0]}</span>
                  </div>

                  <div className="flex items-end justify-between gap-4 text-white">
                    <div className="min-w-0">
                      <div className="text-3xl font-semibold tracking-[0.2em]">#{formatRoomId(room.id)}</div>
                      <div className="mt-2 text-sm text-white/70">房间编号</div>
                    </div>
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-white/15 bg-black/45 text-white/90">
                      <img src={images.ChatBubble} alt="" className="h-9 w-9 object-contain opacity-90" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex flex-wrap items-start gap-4">
                <div className="mt-1 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/[0.03] text-zinc-100">
                  <BubbleIcon className="h-6 w-6" />
                </div>
                <div className="min-w-0 flex-1">
                  {editing ? (
                    <input
                      value={form.name}
                      maxLength={8}
                      onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                      className="w-full border-0 border-b border-white/15 bg-transparent px-0 pb-2 text-[28px] font-semibold text-white outline-none ring-0 placeholder:text-zinc-600 focus:border-white/40"
                      autoFocus
                    />
                  ) : (
                    <h2 className="truncate text-[28px] font-semibold text-white">{currentTitle}</h2>
                  )}
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <Badge>{roomTags[0]}</Badge>
                    <Badge>房间 #{formatRoomId(room.id)}</Badge>
                    <Badge>{displayOwnerName}</Badge>
                  </div>
                </div>
              </div>

              <p className="max-w-2xl text-[15px] leading-8 text-zinc-200">
                {editing ? (
                  <input
                    value={form.description}
                    maxLength={20}
                    onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                    className="w-full border-0 border-b border-white/15 bg-transparent px-0 pb-2 text-base text-zinc-100 outline-none ring-0 placeholder:text-zinc-600 focus:border-white/40"
                  />
                ) : (
                  room.description || '暂无简介'
                )}
              </p>

              <div className="overflow-hidden rounded-lg border border-white/10 bg-white/[0.03]">
                <div className="grid divide-x divide-white/10 sm:grid-cols-2 xl:grid-cols-4">
                  <StatItem icon={<UserIcon className="h-5 w-5" />} label="当前成员" value={`${room.online_members ?? 0} / ${room.max_members}`} />
                  <StatItem icon={<TrendIcon className="h-5 w-5" />} label="最大人数" value={room.max_members} />
                  <StatItem icon={<ChartIcon className="h-5 w-5" />} label="累计参与者" value={room.peak_online_members} />
                  <StatItem icon={<ClockIcon className="h-5 w-5" />} label="创建日期" value={formatRoomDate(room.created_at)} />
                </div>
              </div>
            </div>
          </div>

          <div className="grid gap-4">
            <Section
              title="房间说明"
              icon={<span className="inline-flex h-5 w-5 items-center justify-center text-base leading-none">▤</span>}
            >
              {editing ? (
                <div className="space-y-2">
                  <textarea
                    value={form.notice}
                    maxLength={200}
                    rows={4}
                    onChange={(event) => setForm((current) => ({ ...current, notice: event.target.value }))}
                    className="min-h-[120px] w-full resize-none border border-white/10 bg-black/40 px-3 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-600 focus:border-white/30"
                  />
                  <div className="text-xs text-zinc-500">{form.notice.length}/200</div>
                </div>
              ) : (
                <div className="whitespace-pre-wrap text-zinc-200">{room.notice || '暂无说明'}</div>
              )}
            </Section>

            <Section
              title="房间规则"
              icon={<ShieldIcon className="h-5 w-5" />}
            >
              {editing ? (
                <div className="space-y-2">
                  <textarea
                    value={form.rules}
                    maxLength={200}
                    rows={4}
                    onChange={(event) => setForm((current) => ({ ...current, rules: event.target.value }))}
                    className="min-h-[120px] w-full resize-none border border-white/10 bg-black/40 px-3 py-3 text-sm text-zinc-100 outline-none placeholder:text-zinc-600 focus:border-white/30"
                  />
                  <div className="text-xs text-zinc-500">{form.rules.length}/200</div>
                </div>
              ) : (
                <div className="whitespace-pre-wrap text-zinc-200">{room.rules || '暂无规则'}</div>
              )}
            </Section>

            <Section
              title="房间标签"
              icon={<TagIcon className="h-5 w-5" />}
            >
              <div className="flex flex-wrap gap-2">
                {roomTags.map((tag) => (
                  <Badge key={tag}>{tag}</Badge>
                ))}
              </div>
            </Section>
          </div>
        </div>

        <div className="border-t border-white/10 px-4 py-4 sm:px-5">
          {isOwner ? (
            <>
              <div className="flex flex-col gap-3 sm:flex-row">
                {editing ? (
                  <>
                    <button
                      type="button"
                      disabled={updatingRoom}
                      onClick={handleSave}
                      className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/20 bg-white px-4 text-sm font-semibold text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-500"
                    >
                      <PencilIcon className="h-4 w-4" />
                      保存修改
                    </button>
                    <button
                      type="button"
                      disabled={updatingRoom}
                      onClick={handleCancel}
                      className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/15 bg-black/30 px-4 text-sm font-medium text-zinc-100 transition hover:border-white/30 disabled:cursor-not-allowed disabled:text-zinc-600"
                    >
                      取消
                      </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={handleClose}
                      className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/15 bg-black/30 px-4 text-sm font-medium text-zinc-100 transition hover:border-white/30"
                    >
                      关闭
                    </button>
                    <button
                      type="button"
                      onClick={beginEdit}
                      className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/20 bg-white px-4 text-sm font-semibold text-black transition hover:bg-zinc-200"
                    >
                      <PencilIcon className="h-4 w-4" />
                      编辑房间
                    </button>
                  </>
                )}
              </div>

              {!editing ? (
                <div className="mt-3 flex justify-end">
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={deletingRoom}
                    className="inline-flex items-center gap-2 text-sm text-red-300 transition hover:text-red-200 disabled:cursor-not-allowed disabled:text-zinc-600"
                  >
                    <TrashIcon className="h-4 w-4" />
                    {deletingRoom ? '删除中...' : '删除房间'}
                  </button>
                </div>
              ) : null}
            </>
          ) : (
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={handleClose}
                className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/15 bg-black/30 px-4 text-sm font-medium text-zinc-100 transition hover:border-white/30"
              >
                关闭
              </button>
              <button
                type="button"
                onClick={handleClose}
                className="inline-flex h-12 flex-1 items-center justify-center gap-2 border border-white/20 bg-white px-4 text-sm font-semibold text-black transition hover:bg-zinc-200"
              >
                返回聊天
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
