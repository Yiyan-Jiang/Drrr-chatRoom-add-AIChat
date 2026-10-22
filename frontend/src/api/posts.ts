/** 定义帖子与评论数据，并封装发布、查询、点赞和收藏请求。 */
import { apiClient } from './client'

/** 帖子与评论引用的作者资料。 */
export interface PostAuthor {
  /** 服务端记录编号。 */
  id: number
  /** 登录用户名。 */
  username: string
  /** 用户昵称。 */
  nickname?: string | null
  /** 用户简介。 */
  bio?: string
  /** 头像主题键。 */
  avatar_key: string
  /** 服务端创建时间字符串。 */
  created_at: string
}

/** 帖子列表中的内容摘要、交互统计和当前用户点赞状态。 */
export interface PostListItem {
  /** 服务端记录编号。 */
  id: number
  /** 帖子标题。 */
  title: string
  /** 正文摘要。 */
  content_preview: string
  /** 作者资料；作者不可用时可为空。 */
  author: PostAuthor | null
  /** 评论数量。 */
  comments_count: number
  /** 点赞数量。 */
  likes_count: number
  /** 收藏数量。 */
  favorites_count: number
  /** 当前用户是否已点赞。 */
  liked_by_me: boolean
  /** 服务端创建时间字符串。 */
  created_at: string
  /** 服务端最近更新时间字符串。 */
  updated_at: string
}

/** 帖子完整正文与当前用户收藏状态。 */
export interface PostDetail extends PostListItem {
  /** 帖子完整 Markdown 正文。 */
  content: string
  /** 当前用户是否已收藏。 */
  favorited_by_me: boolean
}

/** 帖子评论及其作者与时间。 */
export interface PostComment {
  /** 服务端记录编号。 */
  id: number
  /** 所属帖子编号。 */
  post_id: number
  /** 评论正文。 */
  content: string
  /** 作者资料；作者不可用时可为空。 */
  author: PostAuthor | null
  /** 服务端创建时间字符串。 */
  created_at: string
  /** 服务端最近更新时间字符串。 */
  updated_at: string
}

/** 个人评论列表中附带所属帖子摘要的评论。 */
export interface PostCommentListItem extends PostComment {
  /** 所属帖子标题。 */
  post_title: string
  /** 所属帖子正文摘要。 */
  post_content_preview: string
}

/** 帖子列表的游标分页响应。 */
export interface PaginatedPostsResponse {
  /** 当前页记录。 */
  items: PostListItem[]
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
  /** 下一页查询使用的记录游标。 */
  next_cursor: number | null
}

/** 帖子评论的游标分页响应。 */
export interface PaginatedCommentsResponse {
  /** 当前页记录。 */
  items: PostComment[]
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
  /** 下一页查询使用的记录游标。 */
  next_cursor: number | null
}

/** 个人评论列表的游标分页响应。 */
export interface PaginatedMyCommentsResponse {
  /** 当前页记录。 */
  items: PostCommentListItem[]
  /** 服务端是否还有更早或后续的记录。 */
  has_more: boolean
  /** 下一页查询使用的记录游标。 */
  next_cursor: number | null
}

/** 发布帖子的标题和 Markdown 正文。 */
export interface CreatePostPayload {
  /** 帖子标题。 */
  title: string
  /** 帖子 Markdown 正文。 */
  content: string
}

/** 发布帖子评论的文本请求。 */
export interface CreateCommentPayload {
  /** 评论正文。 */
  content: string
}

/** 帖子、评论、点赞和收藏操作接口。 */
export const postsApi = {
  /**
   * 按游标查询帖子列表。
   * @param params - 记录游标和数量上限。
   * @returns 帖子分页。
   */
  list: async (params?: {
    /** 继续查询帖子列表使用的记录编号游标。 */ cursor?: number
    /** 本次最多返回的帖子数量。 */ limit?: number
    /** 仅查询当前用户好友发布的帖子。 */ friends_only?: boolean
  }): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>('/posts/', {
      params,
    })
    return data
  },
  /**
   * 发布帖子。
   * @param payload - 帖子标题与 Markdown 正文。
   * @returns 新建帖子详情。
   */
  create: async (payload: CreatePostPayload): Promise<PostDetail> => {
    const { data } = await apiClient.post<PostDetail>('/posts/', payload)
    return data
  },
  /**
   * 查询帖子详情。
   * @param postId - 帖子编号。
   * @returns 帖子详情。
   */
  get: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.get<PostDetail>(`/posts/${postId}`)
    return data
  },
  /**
   * 删除指定帖子。
   * @param postId - 帖子编号。
   * @returns 删除请求完成后结束的 Promise。
   */
  delete: async (postId: number): Promise<void> => {
    await apiClient.delete(`/posts/${postId}`)
  },
  /**
   * 按游标查询帖子的评论。
   * @param postId - 帖子编号。
   * @param params - 评论游标和数量上限。
   * @returns 评论分页。
   */
  listComments: async (
    postId: number,
    params?: {
      /** 继续查询评论列表使用的记录编号游标。 */ cursor?: number
      /** 本次最多返回的评论数量。 */ limit?: number
    },
  ): Promise<PaginatedCommentsResponse> => {
    const { data } = await apiClient.get<PaginatedCommentsResponse>(
      `/posts/${postId}/comments`,
      { params },
    )
    return data
  },
  /**
   * 向帖子发表评论。
   * @param postId - 帖子编号。
   * @param payload - 评论正文。
   * @returns 新建评论。
   */
  createComment: async (
    postId: number,
    payload: CreateCommentPayload,
  ): Promise<PostComment> => {
    const { data } = await apiClient.post<PostComment>(
      `/posts/${postId}/comments`,
      payload,
    )
    return data
  },
  /**
   * 为帖子点赞。
   * @param postId - 帖子编号。
   * @returns 更新后的帖子详情。
   */
  like: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.put<PostDetail>(`/posts/${postId}/like`)
    return data
  },
  /**
   * 取消帖子点赞。
   * @param postId - 帖子编号。
   * @returns 更新后的帖子详情。
   */
  unlike: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.delete<PostDetail>(`/posts/${postId}/like`)
    return data
  },
  /**
   * 收藏帖子。
   * @param postId - 帖子编号。
   * @returns 更新后的帖子详情。
   */
  favorite: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.put<PostDetail>(
      `/posts/${postId}/favorite`,
    )
    return data
  },
  /**
   * 取消收藏帖子。
   * @param postId - 帖子编号。
   * @returns 更新后的帖子详情。
   */
  unfavorite: async (postId: number): Promise<PostDetail> => {
    const { data } = await apiClient.delete<PostDetail>(
      `/posts/${postId}/favorite`,
    )
    return data
  },
  /**
   * 查询当前用户收藏的帖子。
   * @param params - 记录游标和数量上限。
   * @returns 帖子分页。
   */
  listMyFavorites: async (params?: {
    /** 继续查询帖子列表使用的记录编号游标。 */ cursor?: number
    /** 本次最多返回的帖子数量。 */ limit?: number
  }): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>(
      '/posts/favorites/mine',
      {
        params,
      },
    )
    return data
  },
  /**
   * 查询当前用户发布的帖子。
   * @param params - 记录游标和数量上限。
   * @returns 帖子分页。
   */
  listMine: async (params?: {
    /** 继续查询帖子列表使用的记录编号游标。 */ cursor?: number
    /** 本次最多返回的帖子数量。 */ limit?: number
  }): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>(
      '/posts/mine',
      {
        params,
      },
    )
    return data
  },
  /**
   * 查询当前用户点赞的帖子。
   * @param params - 记录游标和数量上限。
   * @returns 帖子分页。
   */
  listMyLikes: async (params?: {
    /** 继续查询帖子列表使用的记录编号游标。 */ cursor?: number
    /** 本次最多返回的帖子数量。 */ limit?: number
  }): Promise<PaginatedPostsResponse> => {
    const { data } = await apiClient.get<PaginatedPostsResponse>(
      '/posts/likes/mine',
      {
        params,
      },
    )
    return data
  },
  /**
   * 查询当前用户发表的评论及所属帖子摘要。
   * @param params - 记录游标和数量上限。
   * @returns 个人评论分页。
   */
  listMyComments: async (params?: {
    /** 继续查询评论列表使用的记录编号游标。 */ cursor?: number
    /** 本次最多返回的评论数量。 */ limit?: number
  }): Promise<PaginatedMyCommentsResponse> => {
    const { data } = await apiClient.get<PaginatedMyCommentsResponse>(
      '/posts/comments/mine',
      {
        params,
      },
    )
    return data
  },
}
