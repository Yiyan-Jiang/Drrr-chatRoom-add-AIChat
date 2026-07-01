import type { PostAuthor } from '@/api'
import { getUserDisplayName } from '@/utils/userDisplayName'

export function getPostAuthorName(author: PostAuthor | null): string {
  return author ? getUserDisplayName(author) : '已注销用户'
}
