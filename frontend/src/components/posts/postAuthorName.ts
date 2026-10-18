/** 帖子与评论作者名称展示规则。 */
import type { PostAuthor } from '@/api'
import { getUserDisplayName } from '@/utils/userDisplayName'

/**
 * 返回作者显示名，作者为空时返回已注销用户提示。
 * @param author - 帖子或评论作者，注销后可为空。
 * @returns 供帖子与评论界面展示的作者名称。
 */
export function getPostAuthorName(author: PostAuthor | null): string {
  return author ? getUserDisplayName(author) : '已注销用户'
}
