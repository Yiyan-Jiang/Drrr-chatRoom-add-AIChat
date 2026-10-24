/** 以官方海报介绍 DOLLARS 的作品灵感，用产品截图和时间线展示聊天室特色。 */
import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { useStoryMotion } from './useStoryMotion'
import StoryMessage from './StoryMessage'
import './SettingsPage.css'

const ASSETS = '/project-story/assets/'
const REPO = 'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat'

/** 展示起源、产品特色和项目入口；后半页用截图、时间线和 CTA 制造叙事高潮。 */
export default function SettingsPage() {
  const rootRef = useRef<HTMLElement>(null)
  useStoryMotion(rootRef)

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
          <a href="#showcase">产品</a>
          <a href="#journey">旅程</a>
        </nav>
        <Link className="film-nav-enter" to="/home/rooms">
          进入聊天室 <span aria-hidden="true">↗</span>
        </Link>
      </header>

      {/* ── 第一屏：Hero ── */}
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

      {/* ── 第二屏：起源 ── */}
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

      {/* ── 第三屏：产品展示高潮 ── */}
      <section
        className="story-showcase"
        id="showcase"
        aria-labelledby="showcase-title"
      >
        {/* 背景微粒容器 */}
        <div className="story-particles" aria-hidden="true" />

        <div className="story-showcase-intro anim-fade-up">
          <h2 id="showcase-title">
            不只是聊天。
            <br />
            <span>是你的深夜据点。</span>
          </h2>
          <p>
            一个昵称，一枚头像，一句「晚上好」。
            <br />
            剩下的，交给对话。
          </p>
        </div>

        {/* 聊天气泡编排 —— 引入部分 */}
        <div
          className="story-voices"
          aria-label="使用真实聊天样式编排的示例对话"
        >
          <div className="story-voice story-voice-one anim-fade-up">
            <StoryMessage avatar="setton" name="夜行者">
              这个点，还有人醒着吗？
            </StoryMessage>
          </div>
          <div className="story-voice story-voice-two anim-fade-up">
            <StoryMessage avatar="kanra" name="折原" reverse>
              在。刚从城市的另一端回来。
            </StoryMessage>
          </div>
          <div className="story-voice story-voice-three anim-fade-up">
            <StoryMessage avatar="zawa" name="路过的人">
              那就坐一会儿，说说今天吧。
            </StoryMessage>
          </div>
        </div>

        {/* 产品截图 —— 视觉高潮 */}
        <figure className="story-product-frame anim-fade-up">
          <div className="story-product-glow" aria-hidden="true" />
          <img
            src={`${ASSETS}chat-room.png`}
            alt="DOLLARS 聊天室真实运行截图：多人实时对话界面"
            loading="lazy"
          />
          <figcaption>真实运行中的 DOLLARS 聊天室</figcaption>
        </figure>

        {/* 产品特色卡片 */}
        <div className="story-features">
          <article className="story-feature-card anim-fade-up">
            <div className="story-feature-icon" aria-hidden="true">
              ⚡
            </div>
            <h3>实时消息</h3>
            <p>
              WebSocket 双向通信，消息秒达。
              <br />
              乐观更新 + 回执确认，不丢失每一句。
            </p>
          </article>
          <article className="story-feature-card anim-fade-up">
            <div className="story-feature-icon" aria-hidden="true">
              🎨
            </div>
            <h3>多主题气泡</h3>
            <p>
              8 套角色主题，独立头像与气泡贴图。
              <br />
              选一个最像你的身份。
            </p>
          </article>
          <article className="story-feature-card anim-fade-up">
            <div className="story-feature-icon" aria-hidden="true">
              👥
            </div>
            <h3>好友与私信</h3>
            <p>
              添加好友，发起私聊。
              <br />
              从公共房间到私密对话，一步之遥。
            </p>
          </article>
        </div>
      </section>

      {/* ── 第四屏：消息旅程时间线 ── */}
      <section
        className="story-journey"
        id="journey"
        aria-labelledby="journey-title"
        data-phase="0"
      >
        <div className="story-journey-heading anim-fade-up">
          <h2 id="journey-title">
            一句话的旅程。
          </h2>
          <p>从按下发送，到再次相见。</p>
        </div>

        <div className="story-timeline">
          {/* 左侧 sticky 消息 */}
          <div className="story-timeline-sticky">
            <div className="story-travelling-message">
              <span className="story-message-echo" aria-hidden="true">
                晚上好。
              </span>
              <StoryMessage avatar="kanra" name="折原">
                晚上好。
              </StoryMessage>
              <div className="story-pulse" aria-hidden="true" />
              <div className="story-phase-status" aria-label="消息流转示意">
                <span>等待确认</span>
                <span>已保存 · 已确认</span>
                <span>再次连接，仍在这里</span>
              </div>
            </div>
          </div>

          {/* 右侧时间线节点 */}
          <div className="story-timeline-track">
            <div className="story-timeline-line" aria-hidden="true" />

            <article className="story-timeline-node anim-fade-up" data-phase="0">
              <div className="story-timeline-dot" aria-hidden="true">
                <span />
              </div>
              <div className="story-timeline-content">
                <h3>
                  发送
                  <span>· 先出现在你的眼前</span>
                </h3>
                <p>
                  按下发送，问候先出现在自己的屏幕。乐观更新让对话不等待——用客户端编号关联回执，10 秒未收到回执标记失败。
                </p>
              </div>
            </article>

            <article className="story-timeline-node anim-fade-up" data-phase="1">
              <div className="story-timeline-dot" aria-hidden="true">
                <span />
              </div>
              <div className="story-timeline-content">
                <h3>
                  确认
                  <span>· 被保存，再传向房间</span>
                </h3>
                <p>
                  数据库事务提交后才发送回执与房间广播。确认表示服务器已保存——这句话被安全地交给了所有在场的人。
                </p>
              </div>
            </article>

            <article className="story-timeline-node anim-fade-up" data-phase="2">
              <div className="story-timeline-dot" aria-hidden="true">
                <span />
              </div>
              <div className="story-timeline-content">
                <h3>
                  重连
                  <span>· 短暂离开，也能接着聊</span>
                </h3>
                <p>
                  重新连接时重新加入房间，分页读取历史并合并已有消息。把对话接回离开的地方——这句「晚上好」，依然在这里等你。
                </p>
              </div>
            </article>
          </div>
        </div>
      </section>

      {/* ── 第五屏：沉浸式结尾 CTA ── */}
      <section className="story-finale" id="enter" aria-labelledby="finale-title">
        <div className="story-finale-particles" aria-hidden="true" />
        <div className="story-finale-content anim-fade-up">
          <p className="story-finale-lead">有人说了「晚上好」。</p>
          <h2 id="finale-title">
            下一句，
            <br />
            <span>换你来说。</span>
          </h2>
          <Link className="story-finale-cta" to="/home/rooms">
            进入聊天室
            <span aria-hidden="true">↗</span>
          </Link>
        </div>
        <div className="story-finale-cards">
          <Link className="story-finale-card anim-fade-up" to="/friends">
            <span className="story-finale-card-icon" aria-hidden="true">💬</span>
            <span className="story-finale-card-label">和好友继续</span>
            <span className="story-finale-card-arrow" aria-hidden="true">↗</span>
          </Link>
          <Link className="story-finale-card anim-fade-up" to="/home/posts">
            <span className="story-finale-card-icon" aria-hidden="true">📝</span>
            <span className="story-finale-card-label">把想法留下</span>
            <span className="story-finale-card-arrow" aria-hidden="true">↗</span>
          </Link>
          <a
            className="story-finale-card anim-fade-up"
            href={REPO}
            target="_blank"
            rel="noreferrer"
          >
            <span className="story-finale-card-icon" aria-hidden="true">⚙</span>
            <span className="story-finale-card-label">探索 GitHub</span>
            <span className="story-finale-card-arrow" aria-hidden="true">↗</span>
          </a>
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
