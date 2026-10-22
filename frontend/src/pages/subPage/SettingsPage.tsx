/** 以官方海报介绍 DOLLARS 的作品灵感与项目中的交流方式。 */
import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStoryMotion } from './useStoryMotion'
import './SettingsPage.css'

const ASSETS = '/project-story/assets/'
const REPO = 'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat'

/** 消息演示内容依据真实发送回执与重连回补实现，不发起业务请求。 */
const MESSAGE_STEPS = [
  {
    label: '发送',
    title: '先让问候出现在眼前。',
    description:
      '按下发送，消息立即出现在自己的对话中。此时还在等待服务器确认。',
    status: '等待回执',
    detail:
      '界面先显示待发送消息，并用客户端消息编号关联后续回执；10 秒未收到回执会标记失败。',
  },
  {
    label: '确认',
    title: '被保存，才算有了回应。',
    description:
      '服务器保存消息后，向发送者返回确认，再把消息广播给房间中的人。',
    status: '已保存 · 已确认',
    detail:
      '数据库事务提交后，Socket.IO 才发送确认与房间广播。确认代表服务器已保存，不代表对方已读。',
  },
  {
    label: '重连',
    title: '短暂离线，对话还能接上。',
    description: '重新连上房间后，读取历史消息，补回断开期间错过的内容。',
    status: '历史已回补',
    detail:
      '客户端重入房间，分页读取历史并合并已有消息，让重复记录不会在界面出现两次。',
  },
]

/** 展示起源、聊天灵感和项目入口；海报轻微视差不改变阅读顺序。 */
export default function SettingsPage() {
  const rootRef = useRef<HTMLElement>(null)
  useStoryMotion(rootRef)
  const [messageStep, setMessageStep] = useState(0)
  const currentStep = MESSAGE_STEPS[messageStep]

  return (
    <main
      className="drrr-film"
      ref={rootRef}
      aria-label="DOLLARS 起源与聊天故事"
    >
      <header className="film-nav">
        <a className="film-brand" href="#opening" aria-label="DOLLARS 回到开端">
          D<span>.</span>
        </a>
        <nav aria-label="项目故事导航">
          <a href="#origin">起源</a>
          <a href="#conversation">聊天</a>
        </nav>
        <Link className="film-nav-enter" to="/home/rooms">
          进入聊天室 <span aria-hidden="true">↗</span>
        </Link>
        <span className="film-progress" aria-hidden="true" />
      </header>

      <section
        className="film-opening"
        id="opening"
        aria-labelledby="opening-title"
      >
        <div className="film-opening-copy">
          <h1 id="opening-title">
            DOLLARS<span>.</span>
          </h1>
          <p className="film-opening-subtitle">
            一个名字。
            <br />
            无数种<span>相遇。</span>
          </p>
          <p className="film-opening-intro">
            灵感来自《无头骑士异闻录》。
            <br />
            把作品里的线上相遇，变成一间可以走进的聊天室。
          </p>
          <a className="film-scroll" href="#origin">
            <span aria-hidden="true">↓</span> 从起源说起
          </a>
        </div>
        <figure className="film-hero-poster">
          <div className="film-poster-mat">
            <img
              src={`${ASSETS}drrr-keyvisual.jpg`}
              alt="无头骑士异闻录×2 官方群像主视觉海报"
              width="704"
              height="995"
              fetchPriority="high"
            />
          </div>
          <figcaption>
            <span>デュラララ!! × 2</span>
            <span>OFFICIAL KEY VISUAL</span>
          </figcaption>
        </figure>
        <span className="film-opening-outline" aria-hidden="true">
          無色
        </span>
      </section>

      <section
        className="film-origin"
        id="origin"
        aria-labelledby="origin-title"
      >
        <div className="film-origin-heading">
          <div>
            <h2 id="origin-title">
              始于池袋。
              <br />
              <span>延伸到屏幕之外。</span>
            </h2>
          </div>
          <div className="film-origin-body">
            <p>
              《无头骑士异闻录》以池袋为舞台，把不同人物的日常连接在一起。作品中的
              DOLLARS，也让分散的人们通过网络产生联系。
            </p>
            <p>
              这个项目从那种聊天氛围出发：一个昵称、一枚头像、几句对话。先聊起来，再慢慢认识屏幕另一端的人。
            </p>
            <a
              href="https://www.durarara.com/"
              target="_blank"
              rel="noreferrer"
            >
              了解原作 ↗
            </a>
          </div>
        </div>
        <figure className="film-gathering">
          <img
            src={`${ASSETS}drrr-gathering.png`}
            alt="无头骑士异闻录官方特别活动宣传海报，多位角色齐聚一堂"
            width="924"
            height="700"
            loading="lazy"
          />
          <figcaption>
            <span>《デュラララ!!×２》官方宣传主视觉</span>
          </figcaption>
        </figure>
        <p className="film-origin-foot">
          借用作品的灵感，<span>做一个属于现实的聊天空间。</span>
        </p>
      </section>

      <section
        className="film-product"
        id="conversation"
        aria-labelledby="conversation-title"
      >
        <div className="film-product-heading">
          <h2 id="conversation-title">
            从作品里的相遇，
            <br />
            <span>到真正的聊天室。</span>
          </h2>
          <div>
            <p>
              选一间房，带上自己的头像。
              <br />
              有人说起今天，有人接住下一句。
            </p>
            <Link to="/home/rooms">
              找一间房坐坐 <span aria-hidden="true">↗</span>
            </Link>
          </div>
        </div>
        <figure className="film-product-screen">
          <div className="film-screen-bar">
            <span>DOLLARS / 夜行电台</span>
            <span>聊天室实景</span>
          </div>
          <div
            className="film-screen-scroll"
            tabIndex={0}
            role="region"
            aria-label="真实聊天室截图，小屏可横向滚动查看"
          >
            <img
              src={`${ASSETS}chat-room.png`}
              alt="真实聊天室：夜行电台房间的输入框、头像与四条示例对话，最后一句是那么，就从一句晚上好开始。"
              width="1400"
              height="840"
              loading="lazy"
            />
          </div>
          <figcaption>
            独立昵称与头像、房间内的实时对话，都在同一个界面里。
            <span>演示对话</span>
          </figcaption>
        </figure>
        <div className="film-product-caption">
          <p>
            熟悉的头像。<span>自己的声音。</span>
          </p>
          <a href="#message-journey">
            一句话发出之后，发生了什么？ <span aria-hidden="true">↓</span>
          </a>
        </div>
      </section>

      <section
        className="film-journey"
        id="message-journey"
        aria-labelledby="journey-title"
      >
        <div className="film-journey-heading">
          <h2 id="journey-title">
            不止让消息出现。
            <br />
            <span>也让对话留下来。</span>
          </h2>
          <p>
            从屏幕上的一句「晚上好」，
            <br />
            看看这间聊天室如何接住它。
          </p>
        </div>
        <div className="film-journey-layout">
          <div className="film-journey-demo" data-step={messageStep}>
            <div className="film-journey-demo-heading">
              <span>夜行电台</span>
              <span>消息流转演示</span>
            </div>
            <div className="film-journey-message">
              <img
                src={`${ASSETS}avatar-kanra.png`}
                alt=""
                width="48"
                height="48"
              />
              <div>
                <span>折原</span>
                <p>那么，就从一句「晚上好」开始。</p>
              </div>
            </div>
            <div className="film-message-receipt" aria-live="polite">
              <span aria-hidden="true">{messageStep === 0 ? '◌' : '✓'}</span>
              {currentStep.status}
            </div>
            <div className="film-journey-track" aria-hidden="true">
              <span className="is-active">你的屏幕</span>
              <i />
              <span className={messageStep > 0 ? 'is-active' : ''}>
                保存与确认
              </span>
              <i />
              <span className={messageStep > 1 ? 'is-active' : ''}>
                重连后的历史
              </span>
            </div>
          </div>
          <div className="film-journey-explanation">
            <div className="film-step-controls" aria-label="查看消息流转阶段">
              {MESSAGE_STEPS.map((step, index) => (
                <button
                  key={step.label}
                  type="button"
                  aria-pressed={messageStep === index}
                  aria-controls="message-step-content"
                  onClick={() => setMessageStep(index)}
                >
                  <span aria-hidden="true">0{index + 1}</span>
                  {step.label}
                </button>
              ))}
            </div>
            <div id="message-step-content" aria-live="polite">
              <h3>{currentStep.title}</h3>
              <p>{currentStep.description}</p>
            </div>
            <details className="film-engineering" key={messageStep}>
              <summary>
                看看背后的实现 <span aria-hidden="true">＋</span>
              </summary>
              <p>{currentStep.detail}</p>
            </details>
          </div>
        </div>
      </section>

      <section
        className="film-invitation"
        id="enter"
        aria-labelledby="final-title"
      >
        <p>「那么，就从一句晚上好开始。」</p>
        <h2 id="final-title">
          下一句，<span>换你来说。</span>
        </h2>
        <div className="film-invitation-actions">
          <Link className="film-cta" to="/home/rooms">
            进入聊天室 <span aria-hidden="true">↗</span>
          </Link>
          <a href={REPO} target="_blank" rel="noreferrer">
            探索 GitHub ↗
          </a>
        </div>
        <div className="film-continuations">
          <Link to="/friends">聊得来，就加个好友 ↗</Link>
          <Link to="/home/posts">想慢慢说，就写成帖子 ↗</Link>
        </div>
      </section>
      <footer className="film-footer">
        <div>
          <a className="film-brand" href="#opening" aria-label="回到开端">
            D<span>.</span>
          </a>
          <p>个人学习项目 · 非官方作品</p>
          <a href="#opening">回到开端 ↑</a>
        </div>
        <p>
          海报来自{' '}
          <a href="https://www.durarara.com/" target="_blank" rel="noreferrer">
            《デュラララ!!×２》官方网站 ↗
          </a>{' '}
          · 图像版权属于原权利方。
          <br />
          ©2014 成田良悟／KADOKAWA アスキー・メディアワークス刊／池袋ダラーズ
        </p>
      </footer>
    </main>
  )
}
