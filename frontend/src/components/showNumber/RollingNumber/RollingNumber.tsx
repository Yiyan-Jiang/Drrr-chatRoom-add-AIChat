/**
 * @parm 组件用途：展示带滚动动画的注册人数数字。
 */
import Digit from '@/components/showNumber/Digit'

export default function RollingNumber({ value, size = 40 }: { value: number; size?: number }) {
  const formatted = String(value).padStart(6, '0')
  const chars = formatted.split('')
  return (
    <div className="flex" style={{ gap: Math.round(size * 0.1) }}>
      {chars.map((char, i) => (
        <Digit key={`${char}-${i}`} value={char} size={size} />
      ))}
    </div>
  )
}
