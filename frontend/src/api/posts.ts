import { apiClient } from './client'

export interface PostAuthor {
  id: number
  username: string
  nickname?: string | null
  bio?: string
  avatar_key: string
  created_at: string
}

export interface PostListItem {
  id: number
  title: string
  content_preview: string
  author: PostAuthor | null
  comments_count: number
  likes_count: number
  favorites_count: number
  liked_by_me: boolean
  created_at: string
  updated_at: string
}

export interface PostDetail extends PostListItem {
  content: string
  favorited_by_me: boolean
}

export interface PostComment {
  id: number
  post_id: number
  content: string
  author: PostAuthor | null
  created_at: string
  updated_at: string
}

export interface PostCommentListItem extends PostComment {
  post_title: string
  post_content_preview: string
}

export interface PaginatedPostsResponse {
  items: PostListItem[]
  has_more: boolean
  next_cursor: number | null
}

export interface PaginatedCommentsResponse {
  items: PostComment[]
  has_more: boolean
  next_cursor: number | null
}

export interface PaginatedMyCommentsResponse {
  items: PostCommentListItem[]
  has_more: boolean
  next_cursor: number | null
}

export interface CreatePostPayload {
  title: string
  content: string
}

export interface CreateCommentPayload {
  content: string
}

export const postsApi = {
  list: async (params?: { cursor?: number; limit?: number }): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>('/posts/', { params })
    return data
  },
  create: async (payload: CreatePostPayload): Promise<PostDetail> => {
    const { data } = await apiClient.post<PostDetail>('/posts/', payload)
    return data
  },
  get: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.get<PostDetail>(`/posts/${postId}`)
    return data
  },
  delete: async (postId: number): Promise<void> => {
    await apiClient.delete(`/posts/${postId}`)
  },
  listComments: async (
    postId: number,
    params?: { cursor?: number; limit?: number },
  ): Promise<PaginatedCommentsResponse> => {
    const { data } = await apiClient.get<PaginatedCommentsResponse>(
      `/posts/${postId}/comments`,
      { params },
    )
    return data
  },
  createComment: async (postId: number, payload: CreateCommentPayload): Promise<PostComment> => {
    const { data } = await apiClient.post<PostComment>(`/posts/${postId}/comments`, payload)
    return data
  },
  like: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.put<PostDetail>(`/posts/${postId}/like`)
    return data
  },
  unlike: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.delete<PostDetail>(`/posts/${postId}/like`)
    return data
  },
  favorite: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.put<PostDetail>(`/posts/${postId}/favorite`)
    return data
  },
  unfavorite: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.delete<PostDetail>(`/posts/${postId}/favorite`)
    return data
  },
  listMyFavorites: async (
    params?: { cursor?: number; limit?: number },
  ): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>('/posts/favorites/mine', {
      params,
    })
    return data
  },
  listMine: async (
    params?: { cursor?: number; limit?: number },
  ): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>('/posts/mine', {
      params,
    })
    return data
  },
  listMyLikes: async (
    params?: { cursor?: number; limit?: number },
  ): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>('/posts/likes/mine', {
      params,
    })
    return data
  },
  listMyComments: async (
    params?: { cursor?: number; limit?: number },
  ): Promise<PaginatedMyCommentsResponse> => {
    const { data } = await apiClient.get<PaginatedMyCommentsResponse>('/posts/comments/mine', {
      params,
    })
    return data
  },
}
