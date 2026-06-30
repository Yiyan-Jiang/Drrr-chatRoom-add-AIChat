import { useCallback, useEffect, useState } from 'react'
import { postsApi, type PostComment, type PostDetail } from '@/api'

type LoadState = 'idle' | 'loading' | 'success' | 'error'

function getDetailErrorMessage(error: unknown): string {
  const status = typeof error === 'object' && error !== null && 'response' in error
    ? (error as { response?: { status?: number } }).response?.status
    : undefined
  if (status === 404) {
    return '帖子不存在或已被删除。'
  }
  return '暂时无法加载帖子，请稍后重试。'
}

export function usePostDetail(postId: number | null) {
  const [post, setPost] = useState<PostDetail | null>(null)
  const [comments, setComments] = useState<PostComment[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [isMutating, setIsMutating] = useState(false)
  const [commentDraft, setCommentDraft] = useState('')

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
      const next = post.liked_by_me ? await postsApi.unlike(post.id) : await postsApi.like(post.id)
      setPost(next)
    } catch {
      setPost(previous)
      setErrorMessage('点赞失败，请稍后重试。')
    } finally {
      setIsMutating(false)
    }
  }, [isMutating, post])

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

  const submitComment = useCallback(async () => {
    if (!post || !commentDraft.trim()) {
      return
    }
    const content = commentDraft.trim()
    setIsMutating(true)
    try {
      const comment = await postsApi.createComment(post.id, { content })
      setComments((current) => [comment, ...current])
      setPost((current) => current
        ? { ...current, comments_count: current.comments_count + 1 }
        : current)
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
