/**
 * 展示当前注册用户数量。
 */
import { useUserCount } from '@/hooks/useUserCount'
import RollingNumber from '@/components/showNumber/RollingNumber'

/**
 * 加载并展示注册用户数量，同时提供加载、失败提示与重试入口。
 * @param props - 控制数字位及配套文字尺寸的配置。
 */
export default function ShowUser({
  size = 40,
}: {
  /** 数字位高度，单位为像素，默认 40。 */ size?: number
}) {
  const { data, loading, error, refetch } = useUserCount()

  const count = data?.total ?? 0
  const labelFontSize = Math.round(size * 0.35)

  return (
    <div className="text-black" style={{ fontSize: labelFontSize }}>
      {loading && <div>加载中...</div>}

      {error && (
        <div>
          <span>{error}</span>
          <button onClick={refetch}>重试</button>
        </div>
      )}

      {!loading && !error && (
        <div className="flex flex-col items-center">
          <span className="text-[#666]" style={{ fontSize: labelFontSize }}>
            当前已经注册人数：
          </span>
          <RollingNumber value={count} size={size} />
        </div>
      )}
    </div>
  )
}
