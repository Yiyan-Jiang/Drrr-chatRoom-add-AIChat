/** 帖子互动计数配套的 SVG 图标。 */
/** 帖子互动图标的样式配置。 */
type IconProps = {
  /** 附加到图标默认尺寸类之后的样式类。 */
  className?: string
}

/** 渲染使用当前文字颜色描边的点赞图标。 */
export function LikeIcon({ className = '' }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={`h-4 w-4 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M7 10v11" />
      <path d="M15 5.4 14 10h5.7a2 2 0 0 1 2 2.3l-1.4 7a2 2 0 0 1-2 1.7H7" />
      <path d="M7 10H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3" />
      <path d="M14 10V5.4a2 2 0 0 0-3.7-1.1L7 10" />
    </svg>
  )
}

/** 渲染使用当前文字颜色描边的收藏图标。 */
export function FavoriteIcon({ className = '' }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={`h-4 w-4 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M19 21 12 17 5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    </svg>
  )
}

/** 渲染使用当前文字颜色描边的评论图标。 */
export function CommentIcon({ className = '' }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={`h-4 w-4 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
    </svg>
  )
}
