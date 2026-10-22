/**
 * 展示 DOLLARS 项目起点、实时消息链路与工程实现。
 */
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import './SettingsPage.css'

const FLOW_STEPS = [
  '发出 send_message · 示例数据',
  '校验 JWT 身份与房间',
  'SQLAlchemy 提交消息事务',
  'message_ack 返回发送方',
  'new_message 广播到房间',
]

const CHAPTERS = [
  ['origin', '起点'],
  ['idea', '想法'],
  ['flow', '流转'],
  ['experience', '体验'],
  ['engineering', '工程'],
]

/** 展示随设定页滚动展开的 DOLLARS 项目叙事。 */
export default function SettingsPage() {
  const scrollRootRef = useRef<HTMLElement>(null)
  const flowSectionRef = useRef<HTMLElement>(null)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [scrollFlowProgress, setScrollFlowProgress] = useState(0)
  const [activeChapter, setActiveChapter] = useState('')
  const [activeIdeaStep, setActiveIdeaStep] = useState(0)
  const [flowStage, setFlowStage] = useState(0)
  const [flowPlaying, setFlowPlaying] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)

  useEffect(() => {
    const root = scrollRootRef.current
    if (!root) return

    let animationFrame = 0
    const updateScrollState = () => {
      animationFrame = 0
      const maxScroll = root.scrollHeight - root.clientHeight
      setScrollProgress(maxScroll > 0 ? root.scrollTop / maxScroll : 0)

      const rootBounds = root.getBoundingClientRect()
      const ideaSteps = [
        ...root.querySelectorAll<HTMLElement>('[data-idea-step]'),
      ]
      const marker = rootBounds.top + root.clientHeight * 0.52
      let nearestStep = 0
      let nearestDistance = Number.POSITIVE_INFINITY
      ideaSteps.forEach((step, index) => {
        const bounds = step.getBoundingClientRect()
        const distance = Math.abs((bounds.top + bounds.bottom) / 2 - marker)
        if (distance < nearestDistance) {
          nearestDistance = distance
          nearestStep = index
        }
      })
      setActiveIdeaStep(nearestStep)

      const flowSection = flowSectionRef.current
      if (flowSection) {
        const bounds = flowSection.getBoundingClientRect()
        const start = rootBounds.top + root.clientHeight * 0.72
        const end =
          rootBounds.top - flowSection.offsetHeight + root.clientHeight * 0.35
        const range = start - end
        const progress =
          range > 0 ? Math.min(1, Math.max(0, (start - bounds.top) / range)) : 0
        setScrollFlowProgress(progress)
      }
    }

    const scheduleUpdate = () => {
      if (!animationFrame)
        animationFrame = window.requestAnimationFrame(updateScrollState)
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveChapter(
              (entry.target as HTMLElement).dataset.chapter ?? '',
            )
          }
        })
      },
      { root, rootMargin: '-38% 0px -52% 0px' },
    )

    root.querySelectorAll<HTMLElement>('[data-chapter]').forEach((chapter) => {
      observer.observe(chapter)
    })
    root.addEventListener('scroll', scheduleUpdate, { passive: true })
    window.addEventListener('resize', scheduleUpdate, { passive: true })
    updateScrollState()

    return () => {
      root.removeEventListener('scroll', scheduleUpdate)
      window.removeEventListener('resize', scheduleUpdate)
      observer.disconnect()
      if (animationFrame) window.cancelAnimationFrame(animationFrame)
    }
  }, [])

  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    const updatePreference = () => setReducedMotion(query.matches)
    updatePreference()
    query.addEventListener('change', updatePreference)
    return () => query.removeEventListener('change', updatePreference)
  }, [])

  useEffect(() => {
    if (!flowPlaying) return
    const timer = window.setTimeout(
      () => {
        const nextStage = flowStage + 1
        setFlowStage(nextStage)
        if (nextStage >= FLOW_STEPS.length) setFlowPlaying(false)
      },
      reducedMotion ? 120 : 720,
    )
    return () => window.clearTimeout(timer)
  }, [flowPlaying, flowStage, reducedMotion])

  const demoComplete = !flowPlaying && flowStage >= FLOW_STEPS.length
  const flowProgress = flowPlaying
    ? Math.min(1, flowStage / FLOW_STEPS.length)
    : demoComplete
      ? 1
      : scrollFlowProgress
  const visibleFlowStage =
    flowPlaying || demoComplete
      ? Math.min(flowStage, FLOW_STEPS.length - 1)
      : Math.min(
          FLOW_STEPS.length - 1,
          Math.floor(scrollFlowProgress * FLOW_STEPS.length),
        )
  const flowStatus = flowPlaying
    ? (FLOW_STEPS[flowStage] ?? '流程结束 · 未发送真实消息')
    : demoComplete
      ? '流程结束 · 未发送真实消息'
      : scrollFlowProgress > 0.98
        ? '流程完整 · 仅为技术流程示意'
        : '滚动查看流程 · 仅为技术流程示意'

  return (
    <main
      ref={scrollRootRef}
      className="settings-story"
      tabIndex={-1}
      aria-label="DOLLARS 项目故事"
    >
      <header className="settings-story__nav">
        <a
          className="settings-story__wordmark"
          href="#story-top"
          aria-label="回到开端"
        >
          D<span>.</span>
        </a>
        <nav aria-label="项目故事章节">
          {CHAPTERS.map(([id, label]) => (
            <a
              key={id}
              href={'#' + id}
              aria-current={activeChapter === id ? 'location' : undefined}
            >
              {label}
            </a>
          ))}
        </nav>
        <a
          className="settings-story__repo-link"
          href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat"
          target="_blank"
          rel="noreferrer"
        >
          GitHub <span aria-hidden="true">↗</span>
        </a>
        <div className="settings-story__progress" aria-hidden="true">
          <span style={{ transform: 'scaleX(' + scrollProgress + ')' }} />
        </div>
      </header>

      <section
        className="settings-story__hero settings-story__chapter"
        id="story-top"
        data-chapter="top"
        aria-labelledby="story-title"
      >
        <div className="settings-story__hero-copy">
          <p className="settings-story__eyebrow">
            <span />
            一间属于城市的聊天室
          </p>
          <p className="settings-story__hero-brand">DOLLARS</p>
          <h1 id="story-title">
            城市的另一端，
            <br />
            有人与你同频。
          </h1>
          <p className="settings-story__hero-description">
            一间从《无头骑士异闻录》得到灵感的线上聊天室。让相遇发生，让话题延续，也让想法有地方留下。
          </p>
          <div className="settings-story__actions">
            <a
              className="settings-story__button settings-story__button--primary"
              href="#origin"
            >
              沿着故事向下 <span aria-hidden="true">↓</span>
            </a>
            <a
              className="settings-story__button settings-story__button--quiet"
              href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat"
              target="_blank"
              rel="noreferrer"
            >
              进入 GitHub <span aria-hidden="true">↗</span>
            </a>
          </div>
          <div className="settings-story__hero-meta">
            <span>个人学习项目</span>
            <span>React · FastAPI · Socket.IO</span>
          </div>
        </div>
        <figure className="settings-story__hero-art">
          <img
            src="/project-story/assets/drrr-keyvisual.jpg"
            alt="《无头骑士异闻录》官方主视觉"
            fetchPriority="high"
          />
          <div className="settings-story__art-shade" />
          <figcaption>
            <span>01 / AN OPEN CHANNEL</span>
            <span>INSPIRED BY DURARARA!!</span>
          </figcaption>
          <span className="settings-story__art-index" aria-hidden="true">
            池袋 / 线上
          </span>
        </figure>
        <a className="settings-story__scroll-cue" href="#origin">
          <span />
          继续往下，故事才刚开始
        </a>
      </section>

      <section
        className="settings-story__origin settings-story__chapter"
        id="origin"
        data-chapter="origin"
        aria-labelledby="origin-title"
      >
        <div className="settings-story__section-shell settings-story__origin-shell">
          <div className="settings-story__section-label">
            <span>02</span>起点 / THE ORIGIN
          </div>
          <div className="settings-story__origin-content">
            <p className="settings-story__origin-kicker">
              灵感来自一个很简单的问题
            </p>
            <h2 id="origin-title">
              如果一座城市里，
              <br />
              <span>陌生人也能自在开口，</span>
              <br />
              会发生什么？
            </h2>
            <div className="settings-story__origin-foot">
              <p>
                《无头骑士异闻录》里的
                DOLLARS，是一个没有固定边界的网络。这个项目借用了“线上相遇”的想象，把它变成可以亲手进入的聊天室。
              </p>
              <span aria-hidden="true">—</span>
            </div>
            <div className="settings-story__origin-rule">
              <span>一条消息</span>
              <i />
              <span>一次相遇</span>
              <i />
              <span>一段连接</span>
            </div>
          </div>
        </div>
      </section>

      <section
        className="settings-story__idea settings-story__chapter"
        id="idea"
        data-chapter="idea"
        aria-labelledby="idea-title"
      >
        <div className="settings-story__section-shell">
          <div className="settings-story__section-label">
            <span>03</span>想法 / THE IDEA
          </div>
          <div className="settings-story__idea-heading">
            <p className="settings-story__eyebrow">
              一段关系，可以有不止一种落点
            </p>
            <h2 id="idea-title">
              先在这里相遇。
              <br />
              <span>然后，决定如何继续。</span>
            </h2>
          </div>
          <div
            className="settings-story__idea-story"
            data-step={activeIdeaStep}
          >
            <div
              className="settings-story__chat-stage"
              aria-label="示例对话：展示房间、好友和帖子三种连接方式"
            >
              <div className="settings-story__stage-topline">
                <span />
                示例对话
                <span className="settings-story__stage-room"># 夜行电台</span>
              </div>
              <div className="settings-story__stage-ambient settings-story__ambient-one" />
              <div className="settings-story__stage-ambient settings-story__ambient-two" />
              <div className="settings-story__chat-person settings-story__person-left">
                <img src="/project-story/assets/avatar-setton.png" alt="" />
                <span>setton</span>
              </div>
              <div className="settings-story__chat-person settings-story__person-right">
                <img src="/project-story/assets/avatar-kanra.png" alt="" />
                <span>kanra</span>
              </div>
              <div className="settings-story__chat-message settings-story__message-one">
                <span>夜风里总有一些没说完的话。</span>
                <small>23:41</small>
              </div>
              <div className="settings-story__chat-message settings-story__message-two">
                <span>那就先把它们放在这里。</span>
                <small>23:42</small>
              </div>
              <div className="settings-story__chat-message settings-story__message-three">
                <span>明天也可以继续聊。</span>
                <small>23:43</small>
              </div>
              <div className="settings-story__stage-compose">
                <span>写下此刻的想法…</span>
                <span aria-hidden="true">↑</span>
              </div>
              <p className="settings-story__stage-disclaimer">
                示例对话 · 非实时用户消息
              </p>
              <span className="settings-story__stage-orbit settings-story__orbit-a" />
              <span className="settings-story__stage-orbit settings-story__orbit-b" />
            </div>
            <div className="settings-story__idea-steps">
              {[
                {
                  label: 'ROOM / 相遇',
                  title: '先进入一个房间。',
                  body: '不必先认识谁。选择感兴趣的话题，在公共房间里听见彼此，也让一句话自然地找到回应。',
                },
                {
                  label: 'FRIENDS / 继续',
                  title: '把合拍留在房间之外。',
                  body: '遇到聊得来的人，可以发出好友请求。连接从公共对话延伸到私聊，让关系有机会继续。',
                },
                {
                  label: 'POSTS / 留下',
                  title: '让话题不只停在此刻。',
                  body: '写一篇帖子，分享观察、问题或一段经历。离开房间以后，想法仍能被看见和接续。',
                },
              ].map((step, index) => (
                <article
                  className={
                    'settings-story__idea-step' +
                    (activeIdeaStep === index ? ' is-active' : '')
                  }
                  data-idea-step
                  key={step.label}
                  aria-current={activeIdeaStep === index ? 'step' : undefined}
                >
                  <span className="settings-story__step-number">
                    {'0' + (index + 1)}
                  </span>
                  <div>
                    <p className="settings-story__step-label">{step.label}</p>
                    <h3>{step.title}</h3>
                    <p>{step.body}</p>
                  </div>
                  <span
                    className="settings-story__step-symbol"
                    aria-hidden="true"
                  >
                    ↗
                  </span>
                </article>
              ))}
            </div>
          </div>
          <div className="settings-story__idea-endnote">
            <span>从一条消息出发</span>
            <i />
            <span>抵达更多可能</span>
          </div>
        </div>
      </section>

      <section
        ref={flowSectionRef}
        className="settings-story__flow settings-story__chapter"
        id="flow"
        data-chapter="flow"
        aria-labelledby="flow-title"
      >
        <div className="settings-story__section-shell">
          <div className="settings-story__section-label">
            <span>04</span>流转 / THE JOURNEY
          </div>
          <div className="settings-story__flow-heading">
            <p className="settings-story__eyebrow">
              消息如何抵达房间里的每个人
            </p>
            <h2 id="flow-title">
              一句话出发，
              <br />
              <span>经过真实的系统。</span>
            </h2>
            <p>
              前端发出 Socket.IO
              事件。服务端验证身份与房间，再把消息提交到数据库。提交完成后，发送方收到确认，房间里的连接收到广播。
            </p>
          </div>
          <div
            className="settings-story__flow-map"
            aria-label="技术流程示意：发送、校验、保存、确认与广播"
          >
            <svg
              className="settings-story__flow-route settings-story__flow-route--horizontal"
              viewBox="0 0 1000 96"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <path d="M20 48 H980" pathLength="1000" />
              <path
                className="is-active"
                d="M20 48 H980"
                pathLength="1000"
                style={{ strokeDashoffset: 1000 * (1 - flowProgress) }}
              />
            </svg>
            <svg
              className="settings-story__flow-route settings-story__flow-route--vertical"
              viewBox="0 0 20 1000"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <path d="M10 0 V1000" pathLength="1000" />
              <path
                className="is-active"
                d="M10 0 V1000"
                pathLength="1000"
                style={{ strokeDashoffset: 1000 * (1 - flowProgress) }}
              />
            </svg>
            <div className="settings-story__flow-nodes">
              {[
                ['消息发出', 'send_message', 'Socket.IO', '↗'],
                ['身份与房间', 'JWT · room_id', '服务端校验', '✓'],
                ['事务提交', 'SQLAlchemy', 'MySQL', '⌁'],
                ['发送方确认', 'message_ack', '精确回执', '↩'],
                ['房间广播', 'new_message', '已加入的成员', '◎'],
              ].map(([title, event, detail, glyph], index) => (
                <article
                  className={
                    'settings-story__flow-node' +
                    (visibleFlowStage === index ? ' is-current' : '') +
                    (visibleFlowStage > index || flowProgress >= 1
                      ? ' is-done'
                      : '')
                  }
                  key={event}
                >
                  <span className="settings-story__node-index">
                    {'0' + (index + 1)}
                  </span>
                  <span
                    className="settings-story__node-glyph"
                    aria-hidden="true"
                  >
                    {glyph}
                  </span>
                  <p>{title}</p>
                  <code>{event}</code>
                  <small>{detail}</small>
                </article>
              ))}
            </div>
            <div className="settings-story__flow-sample">
              <span aria-hidden="true">“</span>
              <p>
                今晚的风，
                <br />
                好像比昨天慢了一点。
              </p>
              <small>
                <img src="/project-story/assets/avatar-zawa.png" alt="" />
                zawa · 示例消息
              </small>
            </div>
            <p className="settings-story__flow-status" aria-live="polite">
              {flowStatus}
            </p>
          </div>
          <div className="settings-story__flow-controls">
            <button
              className="settings-story__button settings-story__button--outline"
              type="button"
              disabled={flowPlaying}
              aria-busy={flowPlaying}
              onClick={() => {
                setFlowStage(0)
                setFlowPlaying(true)
              }}
            >
              <span aria-hidden="true">▷</span>演示消息流转
            </button>
            <span>技术流程示意 · 不发送真实消息</span>
            <a
              href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/blob/yiyan/feat-root/backend/normal_system/realtime/room_chat.py"
              target="_blank"
              rel="noreferrer"
            >
              查看事件处理代码 ↗
            </a>
          </div>
          <div className="settings-story__flow-caption">
            <span>身份不是装饰。</span>
            <span>持久化不是终点。</span>
            <span>同一条消息，抵达不同的人。</span>
          </div>
        </div>
      </section>

      <section
        className="settings-story__experience settings-story__chapter"
        id="experience"
        data-chapter="experience"
        aria-labelledby="experience-title"
      >
        <div className="settings-story__section-shell">
          <div className="settings-story__section-label">
            <span>05</span>体验 / THE EXPERIENCE
          </div>
          <div className="settings-story__experience-heading">
            <div>
              <p className="settings-story__eyebrow">从想法到可以使用的界面</p>
              <h2 id="experience-title">
                一间房间，
                <br />
                <span>正在这里发生。</span>
              </h2>
            </div>
            <p>
              真实的本机演示界面。房间、在线成员、聊天消息和侧边栏，共同构成一次完整的进入与交流。
            </p>
          </div>
          <figure className="settings-story__product-figure">
            <div className="settings-story__product-frame">
              <div className="settings-story__product-topbar">
                <span className="settings-story__window-dots">
                  <i />
                  <i />
                  <i />
                </span>
                <span>
                  DOLLARS <i>/</i> ROOM
                </span>
                <span>LOCAL DEMO</span>
              </div>
              <img
                src="/project-story/assets/chat-room.png"
                alt="DOLLARS 聊天房间真实界面截图"
                loading="lazy"
              />
              <span className="settings-story__product-corner">
                REAL INTERFACE
                <br />
                <span>01 — ROOM VIEW</span>
              </span>
            </div>
            <figcaption>
              <span>本机演示账号的真实界面</span>
              <span>聊天室 · 在线成员 · 实时消息</span>
            </figcaption>
          </figure>
          <div className="settings-story__experience-links">
            <span>从这里进入真实页面</span>
            <Link to="/home/rooms">
              房间 <span aria-hidden="true">↗</span>
            </Link>
            <Link to="/friends">
              好友 <span aria-hidden="true">↗</span>
            </Link>
            <Link to="/home/posts">
              帖子 <span aria-hidden="true">↗</span>
            </Link>
          </div>
        </div>
      </section>

      <section
        className="settings-story__engineering settings-story__chapter"
        id="engineering"
        data-chapter="engineering"
        aria-labelledby="engineering-title"
      >
        <div className="settings-story__section-shell">
          <div className="settings-story__section-label">
            <span>06</span>工程 / UNDER THE SURFACE
          </div>
          <div className="settings-story__engineering-heading">
            <p className="settings-story__eyebrow">让连接不仅仅“看起来实时”</p>
            <h2 id="engineering-title">
              每一步，都有
              <br />
              <span>清楚的去处。</span>
            </h2>
            <p>
              前端负责交互与状态合并。FastAPI 处理业务规则。Repository 与
              SQLAlchemy 管理数据写入。Socket.IO 把提交结果交给房间成员。
            </p>
          </div>
          <div
            className="settings-story__architecture"
            aria-label="前端通过 HTTP 与 Socket.IO 连接 FastAPI 服务，再由 Repository 与 SQLAlchemy 访问 MySQL"
          >
            <div className="settings-story__architecture-row">
              <div className="settings-story__architecture-unit settings-story__unit-client">
                <span>CLIENT</span>
                <h3>React + TypeScript</h3>
                <p>HTTP / Socket.IO</p>
                <small>界面、重连、消息合并</small>
              </div>
              <span className="settings-story__arch-connector">
                <i>HTTP · REALTIME</i>
                <b />
              </span>
              <div className="settings-story__architecture-unit">
                <span>APPLICATION</span>
                <h3>FastAPI</h3>
                <p>routers → services</p>
                <small>身份、房间与消息规则</small>
              </div>
              <span className="settings-story__arch-connector">
                <i>ASYNC SESSION</i>
                <b />
              </span>
              <div className="settings-story__architecture-unit">
                <span>PERSISTENCE</span>
                <h3>Repository</h3>
                <p>SQLAlchemy → MySQL</p>
                <small>提交后再发送确认</small>
              </div>
            </div>
            <div className="settings-story__architecture-detail">
              <span>DECISION / 01</span>
              <div>
                <h4>确认发生在持久化之后</h4>
                <p>
                  消息服务先提交数据库事务，再发出 <code>message_ack</code> 与{' '}
                  <code>new_message</code>。客户端按{' '}
                  <code>client_message_id</code>{' '}
                  合并回执与广播，避免同一条消息显示两次。
                </p>
              </div>
              <a
                href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/blob/yiyan/feat-root/backend/normal_system/services/message.py"
                target="_blank"
                rel="noreferrer"
              >
                消息服务 ↗
              </a>
            </div>
          </div>
          <div className="settings-story__code-window">
            <div>
              <span>backend / normal_system / realtime / room_chat.py</span>
              <span>ROOM MESSAGE</span>
            </div>
            <pre>
              <code>
                <span># 校验完成后，先持久化，再分发事件</span>
                {'\n'}db_message = await create_message(db, message_create,
                user_id){'\n'}message_data = serialize_message(db_message,
                user).model_dump(mode="json"){'\n\n'}await sio.emit(
                <b>"message_ack"</b>, message_data, to=sid){'\n'}await sio.emit(
                <b>"new_message"</b>, message_data, room=room_name)
              </code>
            </pre>
          </div>
          <div className="settings-story__engineering-foot">
            <span>断线后重新加入房间，并通过 HTTP 分页补齐历史。</span>
            <a
              href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat/blob/yiyan/feat-root/frontend/src/hooks/useRoomChat.ts"
              target="_blank"
              rel="noreferrer"
            >
              查看重连与历史恢复逻辑 ↗
            </a>
          </div>
          <p className="settings-story__history-note">
            仓库名称保留了历史上的 <code>AIChat</code>；当前版本已移除 AI 功能。
          </p>
        </div>
      </section>

      <section
        className="settings-story__closing settings-story__chapter"
        id="closing"
        data-chapter="closing"
        aria-labelledby="closing-title"
      >
        <div className="settings-story__section-shell">
          <div className="settings-story__section-label">
            <span>07</span>继续 / THE NEXT MESSAGE
          </div>
          <div className="settings-story__closing-mark" aria-hidden="true">
            <span>D</span>
            <i />
            <i />
            <i />
          </div>
          <p className="settings-story__eyebrow">一间没有围墙的房间</p>
          <h2 id="closing-title">
            下一句话，
            <br />
            <span>留给你来开始。</span>
          </h2>
          <p className="settings-story__closing-description">
            这是一个仍在生长的个人学习项目。欢迎从源码认识它，也欢迎进入房间，看看一次相遇如何开始。
          </p>
          <div className="settings-story__closing-actions">
            <Link
              className="settings-story__button settings-story__button--primary"
              to="/home/rooms"
            >
              进入聊天室 <span aria-hidden="true">↗</span>
            </Link>
            <a
              className="settings-story__button settings-story__button--quiet"
              href="https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat"
              target="_blank"
              rel="noreferrer"
            >
              探索 GitHub <span aria-hidden="true">↗</span>
            </a>
          </div>
          <div className="settings-story__closing-bottom">
            <span>Built as a personal learning project.</span>
            <span>灵感源自《无头骑士异闻录》</span>
            <a href="#story-top">回到开端 ↑</a>
          </div>
        </div>
      </section>

      <footer className="settings-story__footer">
        <a href="#story-top">
          DOLLARS<span>.</span>
        </a>
        <p>
          官方视觉作品 © 原权利人 ·{' '}
          <a href="https://www.durarara.com/" target="_blank" rel="noreferrer">
            Durarara!! 官方网站 ↗
          </a>
        </p>
        <span>MADE TO MEET, MADE TO TALK.</span>
      </footer>
    </main>
  )
}
