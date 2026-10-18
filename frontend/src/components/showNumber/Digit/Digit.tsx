/**
 * 展示滚动数字中的单个数字位。
 */
export default function Digit({
  value,
  size = 40,
}: {
  /** 单个数字字符，预期为 0 到 9。 */ value: string
  /** 数字位高度，单位为像素，默认 40。 */ size?: number
}) {
  const offset = Number.isNaN(Number(value)) ? 0 : Number(value)
  const width = Math.round(size * 0.8)
  const fontSize = Math.round(size * 0.45)

  return (
    <div
      className="relative overflow-hidden bg-transparent text-[#666] rounded shadow"
      style={{ width, height: size }}
    >
      <div
        className="absolute left-0 w-full transition-transform duration-800 ease-in-out"
        style={{
          transform: `translateY(-${offset * size}px)`,
        }}
      >
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={i}
            className="w-full flex items-center justify-center font-bold"
            style={{ height: size, fontSize }}
          >
            {i}
          </div>
        ))}
      </div>
    </div>
  )
}
