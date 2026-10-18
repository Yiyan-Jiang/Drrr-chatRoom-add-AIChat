/** 更新文章地址锚点，并等待标题元素出现后滚动到对应位置。 */
/** 可替换的标题查找、地址更新和动画帧调度依赖。 */
type ScrollToHeadingDeps = {
  /** 按标题锚点查找 DOM 元素。 */
  getElementById?: (id: string) => HTMLElement | null
  /** 更新浏览器历史与地址锚点。 */
  pushState?: (data: unknown, unused: string, url?: string | URL | null) => void
  /** 在下一动画帧重新查找标题。 */
  requestAnimationFrame?: (callback: FrameRequestCallback) => number
}

/** 标题滚动时的地址更新、等待次数与依赖配置。 */
interface ScrollToHeadingOptions {
  /** 是否同步更新地址栏锚点，默认为 true。 */
  updateHash?: boolean
  /** 标题未出现时最多追加的动画帧查找次数。 */
  retryCount?: number
  /** 可替换的 DOM 和浏览器操作。 */
  deps?: ScrollToHeadingDeps
}

/**
 * 可选更新地址锚点，并在标题出现后平滑滚动到其顶部。
 * @param id - 目标标题的 DOM 编号。
 * @param options - 是否更新锚点、追加查找次数与浏览器操作依赖。
 * @returns 无返回值；后续查找可能通过动画帧异步执行。
 */
export function scrollToHeadingById(
  id: string,
  { updateHash = true, retryCount = 12, deps }: ScrollToHeadingOptions = {},
) {
  const getElementById =
    deps?.getElementById ?? window.document.getElementById.bind(window.document)
  const pushState =
    deps?.pushState ?? window.history.pushState.bind(window.history)
  const requestFrame =
    deps?.requestAnimationFrame ?? window.requestAnimationFrame.bind(window)

  if (updateHash) {
    pushState(null, '', `#${id}`)
  }

  const tryScroll = (remainingAttempts: number) => {
    const target = getElementById(id)

    if (target) {
      target.scrollIntoView({ block: 'start', behavior: 'smooth' })
      return
    }

    if (remainingAttempts <= 0) {
      return
    }

    requestFrame(() => tryScroll(remainingAttempts - 1))
  }

  tryScroll(retryCount)
}
