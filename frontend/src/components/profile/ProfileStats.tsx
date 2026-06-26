/**
 * @parm 组件用途：展示用户资料页的房间数量、峰值和加入天数统计。
 */
import type { ProfileStat } from './profilePageModel'

type ProfileStatsProps = {
  stats: ProfileStat[]
}

export function ProfileStats({ stats }: ProfileStatsProps) {
  return (
    <section className="grid grid-cols-3 gap-3">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="rounded-2xl border border-zinc-800 bg-zinc-950/40 px-4 py-5 text-center sm:text-left"
        >
          <div className="font-mono text-2xl font-semibold tabular-nums text-zinc-100">{stat.value}</div>
          <div className="mt-1 text-xs text-zinc-500">{stat.label}</div>
        </div>
      ))}
    </section>
  )
}
