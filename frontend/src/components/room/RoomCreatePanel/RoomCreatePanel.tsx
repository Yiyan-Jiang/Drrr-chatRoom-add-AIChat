/**
 * @parm 组件用途：展示创建聊天室的折叠表单面板。
 */
import { useState } from 'react'
import type { FormEvent } from 'react'

interface RoomCreatePanelProps {
  creating: boolean
  newRoomName: string
  description: string
  tagInput: string
  minAge: string
  maxAge: string
  maxMembers: string
  onNewRoomNameChange: (value: string) => void
  onDescriptionChange: (value: string) => void
  onTagInputChange: (value: string) => void
  onMinAgeChange: (value: string) => void
  onMaxAgeChange: (value: string) => void
  onMaxMembersChange: (value: string) => void
  onCreateRoom: () => Promise<void>
}

export default function RoomCreatePanel({
  creating,
  newRoomName,
  description,
  tagInput,
  minAge,
  maxAge,
  maxMembers,
  onNewRoomNameChange,
  onDescriptionChange,
  onTagInputChange,
  onMinAgeChange,
  onMaxAgeChange,
  onMaxMembersChange,
  onCreateRoom,
}: RoomCreatePanelProps) {
  const [open, setOpen] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    await onCreateRoom()
  }

  return (
    <div className="absolute bottom-4 right-4 z-20 flex flex-col items-end gap-3">
      {open ? (
        <form
          onSubmit={handleSubmit}
          className="w-[min(92vw,360px)] border border-white bg-[#090909] p-5 text-white shadow-2xl"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-bold">创建房间</h2>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="h-7 w-7 rounded-full border border-white text-sm leading-6 hover:bg-white hover:text-black"
              aria-label="关闭创建房间表单"
            >
              ×
            </button>
          </div>

          <div className="space-y-3">
            <label className="block text-sm">
              <span className="mb-1 block text-gray-300">房间名称</span>
              <input
                value={newRoomName}
                maxLength={8}
                onChange={(event) => onNewRoomNameChange(event.target.value)}
                disabled={creating}
                className="h-9 w-full rounded-sm border border-white bg-black px-3 text-white outline-none disabled:opacity-60"
                placeholder="输入房间名称"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-gray-300">简介</span>
              <textarea
                value={description}
                maxLength={20}
                onChange={(event) => onDescriptionChange(event.target.value)}
                disabled={creating}
                rows={3}
                className="w-full resize-none rounded-sm border border-white bg-black px-3 py-2 text-white outline-none disabled:opacity-60"
                placeholder="简单介绍这个房间"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-gray-300">标签</span>
              <input
                value={tagInput}
                onChange={(event) => onTagInputChange(event.target.value)}
                disabled={creating}
                className="h-9 w-full rounded-sm border border-white bg-black px-3 text-white outline-none disabled:opacity-60"
                placeholder="学习, 游戏, 闲聊"
              />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="block text-sm">
                <span className="mb-1 block text-gray-300">最小年龄</span>
                <input
                  type="number"
                  min={0}
                  value={minAge}
                  onChange={(event) => onMinAgeChange(event.target.value)}
                  disabled={creating}
                  className="h-9 w-full rounded-sm border border-white bg-black px-3 text-white outline-none disabled:opacity-60"
                  placeholder="不限"
                />
              </label>

              <label className="block text-sm">
                <span className="mb-1 block text-gray-300">最大年龄</span>
                <input
                  type="number"
                  min={0}
                  value={maxAge}
                  onChange={(event) => onMaxAgeChange(event.target.value)}
                  disabled={creating}
                  className="h-9 w-full rounded-sm border border-white bg-black px-3 text-white outline-none disabled:opacity-60"
                  placeholder="不限"
                />
              </label>
            </div>

            <label className="block text-sm">
              <span className="mb-1 block text-gray-300">最大人数</span>
              <input
                type="number"
                min={1}
                value={maxMembers}
                onChange={(event) => onMaxMembersChange(event.target.value)}
                disabled={creating}
                className="h-9 w-full rounded-sm border border-white bg-black px-3 text-white outline-none disabled:opacity-60"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={creating}
            className="mt-5 h-9 w-full rounded-md border border-white bg-white font-semibold text-black transition hover:bg-gray-200 disabled:opacity-60"
          >
            {creating ? '创建中...' : '创建'}
          </button>
        </form>
      ) : null}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex h-12 w-12 items-center justify-center rounded-full border border-white bg-pink-100 text-2xl font-bold text-black shadow-lg transition hover:scale-105"
        aria-label={open ? '关闭创建房间表单' : '打开创建房间表单'}
      >
        {open ? '×' : '+'}
      </button>
    </div>
  )
}
