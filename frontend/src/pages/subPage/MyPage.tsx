/**
 * @parm 组件用途：装配我的页面的数据加载、用户操作和资料展示组件。
 */
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { usersApi } from '@/api/users'
import { roomApi } from '@/api/rooms'
import {
  buildConfirmDialog,
  buildProfileStats,
  ConfirmActionDialog,
  OwnedRoomsSection,
  ProfileHeader,
  ProfileStats,
  toProfileForm,
  type ConfirmAction,
  type ProfileForm,
} from '@/components/profile'
import { useAuth } from '@/contexts/AuthContext'
import type { Room } from '@/types/chat'
import { logger } from '@/utils/logger'

export default function MyPage() {
  const { user, updateUser, logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<ProfileForm>(() => toProfileForm(user))
  const [ownedRooms, setOwnedRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deletingAccount, setDeletingAccount] = useState(false)
  const [editing, setEditing] = useState(false)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null)

  useEffect(() => {
    let cancelled = false

    async function loadProfile() {
      try {
        const [currentUser, rooms] = await Promise.all([
          usersApi.getMe(),
          roomApi.listMine(),
        ])
        if (cancelled) return
        updateUser(currentUser)
        setOwnedRooms(rooms)
        setForm(toProfileForm(currentUser))
      } catch (error) {
        logger.error('[profile] failed to load current user', {
          message: error instanceof Error ? error.message : String(error),
        })
        if (!cancelled) toast.error('加载资料失败')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadProfile()
    return () => {
      cancelled = true
    }
  }, [updateUser])

  useEffect(() => {
    if (!pickerOpen) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setPickerOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [pickerOpen])

  useEffect(() => {
    if (!confirmAction) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !deletingAccount) setConfirmAction(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [confirmAction, deletingAccount])

  const normalizedForm = useMemo(
    () => ({
      nickname: form.nickname.trim(),
      bio: form.bio,
      avatarKey: form.avatarKey,
    }),
    [form],
  )
  const hasChanges =
    normalizedForm.nickname !== (user?.nickname || user?.username || '') ||
    normalizedForm.bio !== (user?.bio || '') ||
    normalizedForm.avatarKey !== (user?.avatar_key ?? '')
  const canSave =
    normalizedForm.nickname.length > 0 && normalizedForm.bio.length <= 200 && hasChanges && !saving && !deletingAccount

  const handleSave = async () => {
    if (!normalizedForm.nickname) {
      toast.error('昵称不能为空')
      return
    }
    if (normalizedForm.bio.length > 200) {
      toast.error('简介最多 200 字')
      return
    }

    setSaving(true)
    try {
      const updatedUser = await usersApi.updateMe({
        nickname: normalizedForm.nickname,
        bio: normalizedForm.bio,
        ...(normalizedForm.avatarKey ? { avatar_key: normalizedForm.avatarKey } : {}),
      })
      updateUser(updatedUser)
      setForm(toProfileForm(updatedUser))
      setEditing(false)
      toast.success('资料已保存')
    } catch (error) {
      logger.error('[profile] failed to save current user', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleCancelEdit = () => {
    setForm(toProfileForm(user))
    setPickerOpen(false)
    setEditing(false)
  }

  const handleDeleteAccount = async () => {
    if (!user || deletingAccount) return

    setDeletingAccount(true)
    try {
      await usersApi.delete(user.id)
      toast.success('账号已注销')
      logout()
      navigate('/login', { replace: true })
    } catch (error) {
      logger.error('[profile] failed to delete current user', {
        message: error instanceof Error ? error.message : String(error),
      })
      toast.error('注销账号失败')
    } finally {
      setDeletingAccount(false)
      setConfirmAction(null)
    }
  }

  const handleConfirmAction = async () => {
    if (confirmAction === 'logout') {
      setConfirmAction(null)
      logout()
      navigate('/login', { replace: true })
      return
    }

    if (confirmAction === 'delete') {
      await handleDeleteAccount()
    }
  }

  if (loading && !user) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-zinc-500">
        加载中...
      </div>
    )
  }

  const displayName = user?.nickname || user?.username || '我的页面'
  const stats = buildProfileStats(ownedRooms, user?.created_at)
  const confirmDialog = buildConfirmDialog(confirmAction, deletingAccount)

  return (
    <div className="h-full min-h-0 overflow-auto bg-[#090909] text-zinc-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-12 sm:px-10">
        <ProfileHeader
          user={user}
          form={form}
          displayName={displayName}
          editing={editing}
          pickerOpen={pickerOpen}
          saving={saving}
          deletingAccount={deletingAccount}
          canSave={canSave}
          onFormChange={setForm}
          onPickerOpenChange={setPickerOpen}
          onStartEdit={() => setEditing(true)}
          onCancelEdit={handleCancelEdit}
          onSave={handleSave}
          onLogout={() => setConfirmAction('logout')}
          onDeleteAccount={() => setConfirmAction('delete')}
        />

        <ProfileStats stats={stats} />
        <OwnedRoomsSection rooms={ownedRooms} />

        {confirmDialog && (
          <ConfirmActionDialog
            dialog={confirmDialog}
            deletingAccount={deletingAccount}
            confirmingDelete={confirmAction === 'delete' && deletingAccount}
            onCancel={() => setConfirmAction(null)}
            onConfirm={handleConfirmAction}
          />
        )}
      </div>
    </div>
  )
}
