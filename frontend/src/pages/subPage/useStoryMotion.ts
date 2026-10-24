/** 为设定页提供滚动驱动的入场动画、视差和时间线联动。 */
import { useEffect } from 'react'
import type { RefObject } from 'react'

/**
 * 创建可撤销的页面动效；移动端、减少动态模式保持静态阅读。
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

        // 全局入场动画：所有 .anim-fade-up 元素
        media.add('(prefers-reduced-motion: no-preference)', () => {
          const context = gsap.context(() => {
            gsap.utils
              .toArray<HTMLElement>('.anim-fade-up')
              .forEach((el) => {
                gsap.fromTo(
                  el,
                  { y: 45, opacity: 0 },
                  {
                    y: 0,
                    opacity: 1,
                    duration: 0.9,
                    ease: 'power3.out',
                    scrollTrigger: {
                      trigger: el,
                      scroller: root,
                      start: 'top 88%',
                      once: true,
                    },
                  },
                )
              })
          }, root)
          return () => context.revert()
        })

        // 桌面端增强动效
        media.add(
          '(min-width: 901px) and (min-height: 700px) and (prefers-reduced-motion: no-preference)',
          () => {
            const context = gsap.context(() => {
              // 海报视差
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

              // 背景大字视差
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

              // 群像海报视差
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

              // 聊天气泡序列：依次错速浮入
              gsap.utils
                .toArray<HTMLElement>('.story-voice')
                .forEach((voice, index) => {
                  gsap.fromTo(
                    voice,
                    { y: 40 + index * 12 },
                    {
                      y: -15,
                      ease: 'none',
                      scrollTrigger: {
                        trigger: voice,
                        scroller: root,
                        start: 'top bottom',
                        end: 'bottom 20%',
                        scrub: true,
                      },
                    },
                  )
                })

              // 产品截图视差
              const productFrame = root.querySelector('.story-product-frame')
              if (productFrame) {
                gsap.fromTo(
                  productFrame,
                  { y: 60 },
                  {
                    y: -30,
                    ease: 'none',
                    scrollTrigger: {
                      trigger: productFrame,
                      scroller: root,
                      start: 'top bottom',
                      end: 'bottom top',
                      scrub: true,
                    },
                  },
                )
              }

              // 时间线节点联动：根据滚动位置切换 data-phase
              const journey =
                root.querySelector<HTMLElement>('.story-journey')!
              const timelineNodes = gsap.utils.toArray<HTMLElement>(
                '.story-timeline-node',
              )
              if (journey && timelineNodes.length) {
                ScrollTrigger.create({
                  trigger: '.story-timeline-track',
                  scroller: root,
                  start: 'top center',
                  end: 'bottom center',
                  onUpdate: () => {
                    const middle =
                      root.getBoundingClientRect().top +
                      root.clientHeight / 2
                    const active = timelineNodes.reduce(
                      (index, node, next) =>
                        node.getBoundingClientRect().top <= middle
                          ? next
                          : index,
                      0,
                    )
                    journey.dataset.phase = String(active)
                  },
                })
              }
            }, root)
            return () => context.revert()
          },
        )
        root.dataset.motion = 'ready'
      })
      .catch((error: unknown) => {
        if (disposed) return
        root.dataset.motion = 'unavailable'
        console.warn('页面动效加载失败，保留静态页面。', error)
      })
    return () => {
      disposed = true
      cleanup?.()
      delete root.dataset.motion
    }
  }, [rootRef])
}
