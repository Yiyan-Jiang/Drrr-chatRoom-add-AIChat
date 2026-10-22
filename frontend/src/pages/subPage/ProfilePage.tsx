/** 展示个人分享卡片并提供返回我的页面入口。 */
import { Link } from 'react-router-dom'
import { ProfileShareCard } from '@/components/profile/ProfileShareCard'
import { useAuth } from '@/contexts/AuthContext'

/** 展示当前账号的会员分享卡片。 */
export default function ProfilePage() {
  const { user } = useAuth()

  return (
    <div className="h-full overflow-auto bg-black px-4 py-7 text-zinc-100 sm:px-8">
      <ProfileShareCard user={user} />
      <div className="mx-auto mt-5 max-w-5xl">
        <Link
          to="/my"
          className="inline-block text-sm text-zinc-400 underline underline-offset-4 hover:text-white"
        >
          返回我的页面
        </Link>
      </div>
    </div>
  )
}
