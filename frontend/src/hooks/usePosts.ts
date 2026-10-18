/** 管理帖子列表的加载与新帖创建状态。 */
import { useCallback, useEffect, useState } from 'react'
import { postsApi, type PostListItem } from '@/api'

/** 异步内容加载的阶段状态。 */
type LoadState = 'idle' | 'loading' | 'success' | 'error'

/**
 * 载入前 30 条帖子，并在创建成功后将新帖插入当前列表。
 * @returns 帖子列表、加载与创建状态，以及刷新和创建操作。
 */
export function usePosts() {
  const [posts, setPosts] = useState<PostListItem[]>([])
  const [loadState, setLoadState] = useState<LoadState>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  /** 刷新首批帖子并写入加载或错误状态。 */
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

  /**
   * 发布帖子并在成功后将新帖插入列表；请求错误向调用方抛出。
   * @param payload - 帖子标题与 Markdown 正文。
   * @returns 新建帖子详情。
   */
  const createPost = useCallback(
    async (payload: {
      /** 待发布的帖子标题。 */ title: string
      /** 待发布的 Markdown 帖子正文。 */ content: string
    }) => {
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
    },
    [],
  )

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
