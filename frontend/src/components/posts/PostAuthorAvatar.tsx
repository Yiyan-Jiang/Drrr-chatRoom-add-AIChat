import type { PostAuthor } from '@/api'
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import UserHoverCard from '@/components/user/UserHoverCard'
import { getPostAuthorName } from '@/components/posts/postAuthorName'

type PostAuthorAvatarProps = {
  author: PostAuthor | null
  className?: string
}

export default function PostAuthorAvatar({ author, className = 'h-10 w-10' }: PostAuthorAvatarProps) {
  const authorName = getPostAuthorName(author)
  const avatar = author ? resolveChatAvatarAssets(author.avatar_key).avatar : resolveChatAvatarAssets(null).avatar

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
