/**
 * 展示用户资料页的关键统计。
 */
import type { ProfileStat } from './profilePageModel'

/** 资料页统计展示数据。 */
type ProfileStatsProps = {
  /** 按展示顺序提供的标签和值。 */
  stats: ProfileStat[]
}

/** 按传入顺序展示资料页的统计标签和值。 */
export function ProfileStats({ stats }: ProfileStatsProps) {
  return (
    <section className="grid grid-cols-3 text-center">
      {stats.map((stat, index) => (
        <div
          key={stat.label}
          className={`px-4 py-3 ${index > 0 ? 'border-l border-zinc-700' : ''}`}
        >
          <div className="font-mono text-2xl font-semibold tabular-nums text-zinc-100">
            {stat.value}
          </div>
          <div className="mt-1 text-xs text-zinc-400">{stat.label}</div>
        </div>
      ))}
    </section>
  )
}
