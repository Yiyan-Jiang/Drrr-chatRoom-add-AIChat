/**
 * @parm 组件用途：展示用户资料页的关键统计。
 */
import type { ProfileStat } from './profilePageModel'

type ProfileStatsProps = {
  stats: ProfileStat[]
}

export function ProfileStats({ stats }: ProfileStatsProps) {
  return (
    <section className="grid grid-cols-3 text-center">
      {stats.map((stat, index) => (
        <div key={stat.label} className={`px-4 py-3 ${index > 0 ? 'border-l border-zinc-700' : ''}`}>
          <div className="font-mono text-2xl font-semibold tabular-nums text-zinc-100">{stat.value}</div>
          <div className="mt-1 text-xs text-zinc-400">{stat.label}</div>
        </div>
      ))}
    </section>
  )
}
