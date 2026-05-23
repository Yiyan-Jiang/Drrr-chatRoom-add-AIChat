import { useEffect, useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { images } from '@/assets/assets'
import type { RoomMember, RoomWithMessages, UpdateRoomRequest } from '@/types/chat'

type RoomInfoForm = Required<UpdateRoomRequest>

interface RoomInfoDrawerProps {
  open: boolean
  room: RoomWithMessages
  members: RoomMember[]
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1 text-xs text-zinc-500">{label}</div>
      <div className="text-sm text-zinc-100">{children}</div>
    </div>
  )
}

function MemberAvatar({ avatarKey, username }: { avatarKey?: string | null; username: string }) {
  const assets = resolveChatAvatarAssets(avatarKey)
  return (
    <img
      src={assets.avatar}
      alt={username}
      className="h-7 w-7 border border-zinc-700 object-cover"
    />
  )
}

export default function RoomInfoDrawer({
  open,
  room,
  members,
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
  const ownerName = room.owner?.username || (room.owner_id ? `用户${room.owner_id}` : '未设置')
  const ownerAvatarKey = room.owner?.avatar_key ?? 'kanra'
  const displayedMembers =
    members.length > 0
      ? members
      : room.owner
        ? [{ id: room.owner.id, username: room.owner.username, avatar_key: room.owner.avatar_key ?? 'kanra' }]
        : []

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
      toast.error('房间名只能包含中文、英文、数字、下划线，长度 1 到 8 个字符')
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
    if (!window.confirm('确认删除该房间？删除后不可恢复。')) return
    try {
      await onDeleteRoom()
    } catch (error) {
      const message = error instanceof Error ? error.message : '删除房间失败'
      window.alert(message)
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 px-4">
      <section className="flex max-h-[86vh] w-full max-w-2xl flex-col border border-zinc-700 bg-zinc-950 p-5 shadow-2xl">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div className="flex min-w-0 items-center gap-3">
            <img src={images.ChatBubble} alt="" className="h-10 w-10 object-contain" />
            <div className="min-w-0">
              {editing ? (
                <input
                  value={form.name}
                  maxLength={8}
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                  className="w-full border border-zinc-700 bg-black px-2 py-1 text-lg font-semibold text-white outline-none focus:border-zinc-400"
                />
              ) : (
                <h2 className="truncate text-xl font-semibold text-zinc-100">{room.name}</h2>
              )}
              <p className="text-xs text-zinc-500">room #{room.id}</p>
            </div>
          </div>
          <button
            type="button"
            disabled={deletingRoom}
            className="text-sm text-zinc-400 hover:text-zinc-100 disabled:cursor-not-allowed disabled:text-zinc-700"
            onClick={handleClose}
          >
            close
          </button>
        </div>

        <div className="min-h-0 flex-1 space-y-5 overflow-hidden">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="房主">
              <div className="flex items-center gap-2">
                <MemberAvatar avatarKey={ownerAvatarKey} username={ownerName} />
                <span>{ownerName}</span>
              </div>
            </Field>
            <Field label="创建时间">{new Date(room.created_at).toLocaleString('zh-CN')}</Field>
            <Field label="最大人数">{room.max_members}</Field>
            <Field label="巅峰在线人数">{room.peak_online_members}</Field>
          </div>

          <div className="space-y-4">
            <Field label={`简介 ${editing ? `${form.description.length}/20` : ''}`}>
              {editing ? (
                <input
                  value={form.description}
                  maxLength={20}
                  onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                  className="w-full border border-zinc-700 bg-black px-2 py-2 text-zinc-100 outline-none focus:border-zinc-400"
                />
              ) : (
                room.description || '暂无简介'
              )}
            </Field>

            <Field label={`说明 ${editing ? `${form.notice.length}/200` : ''}`}>
              {editing ? (
                <textarea
                  value={form.notice}
                  maxLength={200}
                  rows={4}
                  onChange={(event) => setForm((current) => ({ ...current, notice: event.target.value }))}
                  className="w-full resize-none border border-zinc-700 bg-black px-2 py-2 text-zinc-100 outline-none focus:border-zinc-400"
                />
              ) : (
                <span className="whitespace-pre-wrap">{room.notice || '点击编辑添加说明'}</span>
              )}
            </Field>

            <Field label={`房间规则 ${editing ? `${form.rules.length}/200` : ''}`}>
              {editing ? (
                <textarea
                  value={form.rules}
                  maxLength={200}
                  rows={4}
                  onChange={(event) => setForm((current) => ({ ...current, rules: event.target.value }))}
                  className="w-full resize-none border border-zinc-700 bg-black px-2 py-2 text-zinc-100 outline-none focus:border-zinc-400"
                />
              ) : (
                <span className="whitespace-pre-wrap">{room.rules || '点击编辑添加规则'}</span>
              )}
            </Field>
          </div>

          <div>
            <div className="mb-2 text-xs text-zinc-500">在线成员（{displayedMembers.length}）</div>
            <ul className="max-h-36 space-y-2 overflow-y-auto pr-1">
              {displayedMembers.map((member) => (
                <li key={member.id} className="flex items-center gap-2 text-sm text-zinc-200">
                  <MemberAvatar avatarKey={member.avatar_key} username={member.username} />
                  <span>{member.username}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {isOwner ? (
          <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800 pt-4">
            <div className="flex gap-2">
              {editing ? (
                <>
                  <button
                    type="button"
                    disabled={updatingRoom}
                    onClick={handleSave}
                    className="h-9 border border-zinc-500 px-4 text-sm font-semibold text-zinc-100 hover:border-white disabled:cursor-not-allowed disabled:text-zinc-600"
                  >
                    保存
                  </button>
                  <button
                    type="button"
                    disabled={updatingRoom}
                    onClick={handleCancel}
                    className="h-9 border border-zinc-700 px-4 text-sm text-zinc-200 hover:border-zinc-500 disabled:cursor-not-allowed disabled:text-zinc-600"
                  >
                    取消
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setForm(toForm(room))
                    setEditing(true)
                  }}
                  className="h-9 border border-zinc-700 px-4 text-sm text-zinc-200 hover:border-zinc-500"
                >
                  编辑
                </button>
              )}
            </div>

            <button
              type="button"
              onClick={handleDelete}
              disabled={deletingRoom}
              className="h-9 bg-red-600 px-4 text-sm font-semibold text-white hover:bg-red-500 disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-500"
            >
              {deletingRoom ? '删除中...' : '删除房间'}
            </button>
          </div>
        ) : null}
      </section>
    </div>
  )
}
