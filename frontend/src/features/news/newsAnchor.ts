type ScrollToHeadingDeps = {
  getElementById?: (id: string) => HTMLElement | null
  pushState?: (data: unknown, unused: string, url?: string | URL | null) => void
  requestAnimationFrame?: (callback: FrameRequestCallback) => number
}

interface ScrollToHeadingOptions {
  updateHash?: boolean
  retryCount?: number
  deps?: ScrollToHeadingDeps
}

export function scrollToHeadingById(
  id: string,
  { updateHash = true, retryCount = 12, deps }: ScrollToHeadingOptions = {},
) {
  const getElementById = deps?.getElementById ?? window.document.getElementById.bind(window.document)
  const pushState = deps?.pushState ?? window.history.pushState.bind(window.history)
  const requestFrame = deps?.requestAnimationFrame ?? window.requestAnimationFrame.bind(window)

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
