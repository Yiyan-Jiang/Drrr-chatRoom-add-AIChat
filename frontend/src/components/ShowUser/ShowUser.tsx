/**
 * @parm 组件用途：展示当前注册用户数量。
 */
import { useUserCount } from '@/hooks/useUserCount'
import RollingNumber from '@/components/showNumber/RollingNumber'

export default function ShowUser({ size = 40 }: { size?: number }) {
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
          <span className='text-[#666]' style={{ fontSize: labelFontSize }}>
            当前已经注册人数：
          </span>
          <RollingNumber value={count} size={size} />
        </div>
      )}
    </div>
  )
}
