/** 为现存作者展示资料卡入口，作者为空时展示默认头像。 */
import type { PostAuthor } from '@/api'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import UserHoverCard from '@/components/user/UserHoverCard'
import { getPostAuthorName } from '@/components/posts/postAuthorName'

/** 作者资料与头像尺寸配置。 */
type PostAuthorAvatarProps = {
  /** 作者资料；为 null 时展示默认头像。 */
  author: PostAuthor | null
  /** 头像尺寸及样式类，默认 h-10 w-10。 */
  className?: string
}

/** 为现存作者展示资料卡入口，作者为空时展示默认头像。 */
export default function PostAuthorAvatar({
  author,
  className = 'h-10 w-10',
}: PostAuthorAvatarProps) {
  const authorName = getPostAuthorName(author)
  const avatar = author
    ? resolveChatAvatarAssets(author.avatar_key).avatar
    : resolveChatAvatarAssets(null).avatar

  return author ? (
    <UserHoverCard
      user={author}
      avatarClassName={className}
      nameClassName="sr-only"
      showName={false}
    />
  ) : (
    <img
      className={`${className} shrink-0 rounded object-cover`}
      src={avatar}
      alt={`${authorName} avatar`}
      loading="lazy"
    />
  )
}
