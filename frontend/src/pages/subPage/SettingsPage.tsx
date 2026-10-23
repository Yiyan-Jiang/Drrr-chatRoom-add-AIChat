/** 以官方海报介绍 DOLLARS 的作品灵感与项目中的交流方式。 */
import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { useStoryMotion } from './useStoryMotion'
import StoryMessage from './StoryMessage'
import './SettingsPage.css'

const ASSETS = '/project-story/assets/'
const REPO = 'https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat'

/** 展示起源、聊天灵感和项目入口；海报轻微视差不改变阅读顺序。 */
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
        className="story-conversation"
        id="conversation"
        aria-labelledby="conversation-title"
      >
        <div className="story-night-word" aria-hidden="true">
          晚安
        </div>
        <h2 id="conversation-title">
          在这里，
          <br />
          总有人接住
          <br />
          <span>你的下一句。</span>
        </h2>
        <div
          className="story-voices"
          aria-label="使用真实聊天样式编排的示例对话"
        >
          <div className="story-voice story-voice-one">
            <StoryMessage avatar="setton" name="夜行者">
              这个点，还有人醒着吗？
            </StoryMessage>
          </div>
          <div className="story-voice story-voice-two">
            <StoryMessage avatar="kanra" name="折原" reverse>
              在。刚从城市的另一端回来。
            </StoryMessage>
          </div>
          <div className="story-voice story-voice-three">
            <StoryMessage avatar="zawa" name="路过的人">
              那就坐一会儿，说说今天吧。
            </StoryMessage>
          </div>
          <div className="story-voice story-voice-four">
            <StoryMessage avatar="kanra" name="折原" reverse>
              那么，就从一句「晚上好」开始。
            </StoryMessage>
          </div>
        </div>
        <div className="story-conversation-bottom">
          <p>
            一个昵称。一枚头像。
            <br />
            <span>剩下的，交给对话。</span>
          </p>
          <Link className="story-composer" to="/home/rooms">
            <span>你的下一句……</span>
            <b>进入聊天室 ↗</b>
          </Link>
        </div>
        <a className="story-follow-message" href="#message-journey">
          跟随这一句问候 <span aria-hidden="true">↓</span>
        </a>
      </section>

      <section
        className="story-afterword"
        id="message-journey"
        aria-labelledby="journey-title"
        data-phase="0"
      >
        <div className="story-afterword-heading">
          <h2 id="journey-title">
            一句话，
            <br />
            <span>不止于此刻。</span>
          </h2>
          <p>从发出，到再次相见。</p>
        </div>
        <div className="story-message-route">
          <div className="story-travelling-message">
            <span className="story-message-echo" aria-hidden="true">
              晚上好。
            </span>
            <StoryMessage avatar="kanra" name="折原">
              晚上好。
            </StoryMessage>
            <div className="story-phase-status" aria-label="消息流转示意">
              <span>等待确认</span>
              <span>已保存 · 已确认</span>
              <span>再次连接，仍在这里</span>
            </div>
            <span className="story-local-note">消息演示</span>
          </div>
          <div className="story-passages">
            <article className="story-passage" data-phase="0">
              <h3>
                先出现在，
                <br />
                <span>你的眼前。</span>
              </h3>
              <p>
                按下发送，问候先出现在自己的屏幕。
                <br />
                等待另一端传回确认。
              </p>
            </article>
            <article className="story-passage" data-phase="1">
              <h3>
                被保存，
                <br />
                <span>再传向房间。</span>
              </h3>
              <p>
                服务器保存消息后返回确认，
                <br />
                再把这句话送进房间里的对话。
              </p>
            </article>
            <article className="story-passage" data-phase="2">
              <h3>
                短暂离开，
                <br />
                <span>也能接着聊。</span>
              </h3>
              <p>
                重新连接时，从历史中补回错过的消息。
                <br />
                把对话接回离开的地方。
              </p>
            </article>
            <details className="story-engineering">
              <summary>
                这句问候背后的设计 <span aria-hidden="true">＋</span>
              </summary>
              <div>
                <p>
                  界面先显示待发送消息，用客户端编号关联回执；10
                  秒未收到回执会标记失败。
                </p>
                <p>
                  数据库事务提交后才发送回执与房间广播。确认表示服务器已保存，不代表对方已读。
                </p>
                <p>
                  重连后重新加入房间，分页读取历史并合并已有消息。这里展示的是本地叙事，不会实际发送消息。
                </p>
              </div>
            </details>
            <div className="story-reply" id="enter">
              <p>有人说了「晚上好」。</p>
              <h2 id="final-title">
                下一句，
                <br />
                <span>换你来说。</span>
              </h2>
              <Link className="film-cta" to="/home/rooms">
                进入聊天室 <span aria-hidden="true">↗</span>
              </Link>
              <div className="film-continuations">
                <Link to="/friends">和好友继续 ↗</Link>
                <Link to="/home/posts">把想法留下 ↗</Link>
                <a href={REPO} target="_blank" rel="noreferrer">
                  探索 GitHub ↗
                </a>
              </div>
            </div>
          </div>
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
