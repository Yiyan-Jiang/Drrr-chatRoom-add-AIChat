/**
 * @parm 组件用途：切换 AI 聊天角色的标签栏。
 */
import type { AICharacter } from '@/types/ai'

export interface AICharacterOption {
  value: AICharacter
  label: string
  desc: string
  color: string
}

interface AICharacterTabsProps {
  characters: AICharacterOption[]
  selected: AICharacter
  onChange: (character: AICharacter) => void
}

function activeClass(color: string) {
  if (color === 'pink') return 'bg-pink-600 text-white'
  if (color === 'blue') return 'bg-blue-600 text-white'
  if (color === 'purple') return 'bg-purple-600 text-white'
  return 'bg-yellow-600 text-white'
}

export default function AICharacterTabs({ characters, selected, onChange }: AICharacterTabsProps) {
  return (
    <div className="border-b border-gray-800 bg-gray-900/50 p-3">
      <div className="mx-auto flex max-w-4xl items-center justify-center gap-2">
        {characters.map((char) => (
          <button
            key={char.value}
            onClick={() => onChange(char.value)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              selected === char.value ? activeClass(char.color) : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            <span>{char.label}</span>
            <span className="text-xs opacity-70">({char.desc})</span>
          </button>
        ))}
      </div>
    </div>
  )
}
