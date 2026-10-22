/** 为海报提供轻微错速视差，不改变起源介绍与聊天内容的阅读顺序。 */
import { useEffect } from 'react'
import type { RefObject } from 'react'

/**
 * 创建可撤销的海报动效；移动端、减少动态模式保持静态阅读。
 * @param rootRef - 项目介绍的独立滚动容器。
 */
export function useStoryMotion(rootRef: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const root = rootRef.current!
    let disposed = false
    let cleanup: (() => void) | undefined
    Promise.all([import('gsap'), import('gsap/ScrollTrigger')])
      .then(([{ gsap }, { ScrollTrigger }]) => {
        if (disposed) return
        gsap.registerPlugin(ScrollTrigger)
        const media = gsap.matchMedia()
        cleanup = () => media.revert()
        media.add(
          '(min-width: 901px) and (min-height: 700px) and (prefers-reduced-motion: no-preference)',
          () => {
            const context = gsap.context(() => {
              gsap.to('.film-progress', {
                scaleX: 1,
                ease: 'none',
                scrollTrigger: {
                  scroller: root,
                  trigger: root,
                  start: 0,
                  end: () => root.scrollHeight - root.clientHeight,
                  scrub: true,
                },
              })
              gsap.fromTo(
                '.film-hero-poster',
                { y: 0, rotation: 5 },
                {
                  y: 75,
                  rotation: 1,
                  ease: 'none',
                  scrollTrigger: {
                    trigger: '.film-opening',
                    scroller: root,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: true,
                  },
                },
              )
              gsap.to('.film-opening-outline', {
                y: -100,
                ease: 'none',
                scrollTrigger: {
                  trigger: '.film-opening',
                  scroller: root,
                  start: 'top top',
                  end: 'bottom top',
                  scrub: true,
                },
              })
              gsap.fromTo(
                '.film-gathering img',
                { y: 45 },
                {
                  y: -25,
                  ease: 'none',
                  scrollTrigger: {
                    trigger: '.film-gathering',
                    scroller: root,
                    start: 'top bottom',
                    end: 'bottom top',
                    scrub: true,
                  },
                },
              )
            }, root)
            return () => context.revert()
          },
        )
        root.dataset.motion = 'ready'
      })
      .catch((error: unknown) => {
        if (disposed) return
        root.dataset.motion = 'unavailable'
        console.warn('海报动效加载失败，保留静态页面。', error)
      })
    return () => {
      disposed = true
      cleanup?.()
      delete root.dataset.motion
    }
  }, [rootRef])
}
