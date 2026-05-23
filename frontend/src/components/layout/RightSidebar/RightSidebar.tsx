/**
 * @parm 组件用途：展示主布局右侧功能入口和提示区。
 */
import { Link } from 'react-router-dom'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { AICharacter } from '@/types/chat'

type AICharacterItem = {
  id: AICharacter
  label: string
  avatarKey: string
}

const AI_CHARACTERS: AICharacterItem[] = [
  { id: 'sakura', label: '小樱', avatarKey: 'pink' },
  { id: 'rin', label: '凛', avatarKey: 'gray' },
  { id: 'mio', label: '澪', avatarKey: 'zaika' },
  { id: 'yang', label: '葵', avatarKey: 'kanra' },
]

export default function RightSidebar() {
  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    console.log('接口待实现')
  }

  return (
    <div className="ml-1 h-[80%] border-2 border-white bg-[#0D0D0D]">
      <form
        action=""
        onSubmit={handleSearch}
        className="mb-2 h-7 w-full border-b border-white bg-[#45474A] leading-7"
      >
        <input
          type="text"
          placeholder="搜索"
          className="h-full w-full border-none px-2 outline-none"
        />
      </form>

      <div className="mb-4 grid grid-cols-3 lg:grid-cols-4">
        {AI_CHARACTERS.map((char) => {
          const assets = resolveChatAvatarAssets(char.avatarKey)

          return (
            <Link
              key={char.id}
              to={`/ai-chat?char=${char.id}`}
              className="flex flex-col items-center py-2 bg-transparent transition hover:scale-105"
            >
              <img
                src={assets.avatar}
                alt={char.label}
                className="h-14 w-14 object-cover mb-0.5"
              />
              <span className="text-xs font-medium text-gray-300">{char.label}</span>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
