import { useCallback, useEffect, useState } from 'react'
import { postsApi, type PostListItem } from '@/api'

type LoadState = 'idle' | 'loading' | 'success' | 'error'

export function usePosts() {
  const [posts, setPosts] = useState<PostListItem[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const loadPosts = useCallback(async () => {
    setLoadState('loading')
    setErrorMessage('')
    try {
      const page = await postsApi.list({ limit: 30 })
      setPosts(page.items)
      setLoadState('success')
    } catch {
      setErrorMessage('暂时无法加载帖子，请稍后重试。')
      setLoadState('error')
    }
  }, [])

  const createPost = useCallback(async (payload: { title: string; content: string }) => {
    setIsCreating(true)
    try {
      const created = await postsApi.create(payload)
      setPosts((current) => [
        {
          id: created.id,
          title: created.title,
          content_preview: created.content_preview,
          author: created.author,
          comments_count: created.comments_count,
          likes_count: created.likes_count,
          favorites_count: created.favorites_count,
          liked_by_me: created.liked_by_me,
          created_at: created.created_at,
          updated_at: created.updated_at,
        },
        ...current,
      ])
      return created
    } finally {
      setIsCreating(false)
    }
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadPosts()
    }, 0)
    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadPosts])

  return {
    posts,
    loadState,
    errorMessage,
    isCreating,
    loadPosts,
    createPost,
  }
}
