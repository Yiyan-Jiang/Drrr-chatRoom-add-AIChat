/**
 * 展示带滚动动画的注册人数数字。
 */
import Digit from '@/components/showNumber/Digit'

/**
 * 将数值补齐到至少六位并逐位展示滚动数字。
 * @param props - 待显示数值和以像素为单位的数字位高度。
 */
export default function RollingNumber({
  value,
  size = 40,
}: {
  /** 待展示的数字值。 */ value: number
  /** 数字位高度，单位为像素，默认 40。 */ size?: number
}) {
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
