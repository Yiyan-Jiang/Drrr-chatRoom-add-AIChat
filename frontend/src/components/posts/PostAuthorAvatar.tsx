import type { PostAuthor } from '@/api'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import { getUserDisplayName } from '@/utils/userDisplayName'

type PostAuthorAvatarProps = {
  author: PostAuthor | null
  className?: string
}

export function getPostAuthorName(author: PostAuthor | null): string {
  return author ? getUserDisplayName(author) : '已注销用户'
}

export default function PostAuthorAvatar({ author, className = 'h-10 w-10' }: PostAuthorAvatarProps) {
  const authorName = getPostAuthorName(author)
  const avatar = author ? resolveChatAvatarAssets(author.avatar_key).avatar : resolveChatAvatarAssets(null).avatar

  return (
    <img
      className={`${className} shrink-0 rounded object-cover`}
      src={avatar}
      alt={`${authorName} avatar`}
      loading="lazy"
    />
  )
}
