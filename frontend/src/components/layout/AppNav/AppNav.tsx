/**
 * @parm 组件用途：展示顶部快速进入房间的导航输入。
 */
import type { FormEvent } from 'react'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { useAuth } from '@/contexts/AuthContext'
import { getUserDisplayName } from '@/utils/userDisplayName'

export default function AppNav() {
  const { user } = useAuth()
  const avatarAssets = resolveChatAvatarAssets(user?.avatar_key)

  const handleSearch = async (event: FormEvent) => {
    event.preventDefault()
    alert('还没做喔')
  }

  return (
    <div className="flex h-10 justify-between">
      <div />

      <div className="flex items-center justify-center gap-5">
        <div className="flex">
          <form action="" onSubmit={handleSearch}>
            <input type="text" className="mr-3 bg-white px-2 text-sm text-black outline-none" />

            <button className="cursor-pointer border-0 font-bold outline-none active:scale-95">检索</button>
          </form>
        </div>

        <div>DOLLARS 移动版</div>

        <img
          src={avatarAssets.avatar}
          alt={user ? `${getUserDisplayName(user)}的头像` : '用户头像'}
          className="h-8 w-8 object-cover"
        />
      </div>
    </div>
  )
}
