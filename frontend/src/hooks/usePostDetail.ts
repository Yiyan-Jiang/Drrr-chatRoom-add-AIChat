/** 管理帖子详情、首批评论、点赞、收藏与评论提交状态。 */
import { useCallback, useEffect, useState } from 'react'
import { postsApi, type PostComment, type PostDetail } from '@/api'

/** 异步内容加载的阶段状态。 */
type LoadState = 'idle' | 'loading' | 'success' | 'error'

/**
 * 将 404 转换为帖子不存在提示，其余错误使用加载失败提示。
 * @param error - 帖子或评论加载请求的错误值。
 * @returns 帖子详情页使用的错误提示。
 */
function getDetailErrorMessage(error: unknown): string {
  const status =
    typeof error === 'object' && error !== null && 'response' in error
      ? (
          error as {
            /** 详情加载错误中可读取的 HTTP 响应。 */ response?: {
              /** 用于识别帖子不存在错误的 HTTP 状态码。 */ status?: number
            }
          }
        ).response?.status
      : undefined
  if (status === 404) {
    return '帖子不存在或已被删除。'
  }
  return '暂时无法加载帖子，请稍后重试。'
}

/**
 * 载入帖子与前 50 条评论，并管理点赞、收藏和评论提交。
 * @param postId - 帖子编号；为空或 0 时写入无效编号提示。
 * @returns 帖子、评论、表单、错误状态和相关操作；点赞或收藏失败时回滚本地修改。
 */
export function usePostDetail(postId: number | null) {
  const [post, setPost] = useState<PostDetail | null>(null)
  const [comments, setComments] = useState<PostComment[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [isMutating, setIsMutating] = useState(false)
  const [commentDraft, setCommentDraft] = useState('')

  /** 并行刷新帖子详情和前 50 条评论，并更新加载状态。 */
  const loadPost = useCallback(async () => {
    if (!postId) {
      setLoadState('error')
      setErrorMessage('帖子编号无效。')
      return
    }

    setLoadState('loading')
    setErrorMessage('')
    try {
      const [nextPost, nextComments] = await Promise.all([
        postsApi.get(postId),
        postsApi.listComments(postId, { limit: 50 }),
      ])
      setPost(nextPost)
      setComments(nextComments.items)
      setLoadState('success')
    } catch (error) {
      setErrorMessage(getDetailErrorMessage(error))
      setLoadState('error')
    }
  }, [postId])

  /** 乐观切换当前帖子的点赞状态；失败时回滚并写入错误提示。 */
  const toggleLike = useCallback(async () => {
    if (!post || isMutating) {
      return
    }
    const previous = post
    setPost({
      ...post,
      liked_by_me: !post.liked_by_me,
      likes_count: post.likes_count + (post.liked_by_me ? -1 : 1),
    })
    setIsMutating(true)
    try {
      const next = post.liked_by_me
        ? await postsApi.unlike(post.id)
        : await postsApi.like(post.id)
      setPost(next)
    } catch {
      setPost(previous)
      setErrorMessage('点赞失败，请稍后重试。')
    } finally {
      setIsMutating(false)
    }
  }, [isMutating, post])

  /** 乐观切换当前帖子的收藏状态；失败时回滚并写入错误提示。 */
  const toggleFavorite = useCallback(async () => {
    if (!post || isMutating) {
      return
    }
    const previous = post
    setPost({
      ...post,
      favorited_by_me: !post.favorited_by_me,
      favorites_count: post.favorites_count + (post.favorited_by_me ? -1 : 1),
    })
    setIsMutating(true)
    try {
      const next = post.favorited_by_me
        ? await postsApi.unfavorite(post.id)
        : await postsApi.favorite(post.id)
      setPost(next)
    } catch {
      setPost(previous)
      setErrorMessage('收藏失败，请稍后重试。')
    } finally {
      setIsMutating(false)
    }
  }, [isMutating, post])

  /** 提交去除首尾空白的评论，成功后更新评论列表并清空草稿。 */
  const submitComment = useCallback(async () => {
    if (!post || !commentDraft.trim()) {
      return
    }
    const content = commentDraft.trim()
    setIsMutating(true)
    try {
      const comment = await postsApi.createComment(post.id, { content })
      setComments((current) => [comment, ...current])
      setPost((current) =>
        current
          ? { ...current, comments_count: current.comments_count + 1 }
          : current,
      )
      setCommentDraft('')
    } catch {
      setErrorMessage('评论失败，请稍后重试。')
    } finally {
      setIsMutating(false)
    }
  }, [commentDraft, post])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadPost()
    }, 0)
    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadPost])

  return {
    post,
    comments,
    loadState,
    errorMessage,
    isMutating,
    commentDraft,
    setCommentDraft,
    loadPost,
    toggleLike,
    toggleFavorite,
    submitComment,
  }
}
