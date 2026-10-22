/** 以官方海报介绍 DOLLARS 的作品灵感与项目中的交流方式。 */
import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { useStoryMotion } from './useStoryMotion'
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
        className="film-conversation"
        id="conversation"
        aria-labelledby="conversation-title"
      >
        <div className="film-conversation-heading">
          <h2 id="conversation-title">
            不必先认识。
            <br />
            <span>从一句话开始。</span>
          </h2>
          <p>
            保留熟悉的昵称、头像与聊天气泡。
            <br />
            让交流从一个话题开始，而不是一份自我介绍。
          </p>
          <span className="film-japanese" aria-hidden="true">
            誰かと、つながる。
          </span>
        </div>
        <div
          className="film-messages"
          aria-label="聊天氛围示例，非实时用户消息"
        >
          <div className="film-message film-question">
            <span className="film-message-person">
              <img
                src={`${ASSETS}avatar-setton.png`}
                alt=""
                width="42"
                height="42"
              />
              <span>
                setton<small>23:41</small>
              </span>
            </span>
            <p>晚上好。今天有什么想聊的吗？</p>
          </div>
          <div className="film-message film-answer">
            <span className="film-message-person">
              <img
                src={`${ASSETS}avatar-kanra.png`}
                alt=""
                width="42"
                height="42"
              />
              <span>
                kanra<small>23:42</small>
              </span>
            </span>
            <p>有。就从刚刚遇见的事说起吧。</p>
          </div>
        </div>
      </section>

      <section className="film-project" aria-labelledby="project-title">
        <div>
          <h2 id="project-title">
            让对话，<span>有地方继续。</span>
          </h2>
        </div>
        <div className="film-destinations">
          <Link to="/home/rooms">
            <span>01 / ROOM</span>
            <h3>
              在房间相遇 <b aria-hidden="true">↗</b>
            </h3>
            <p>选择话题，与房间里的成员实时聊天。</p>
          </Link>
          <Link to="/friends">
            <span>02 / FRIENDS</span>
            <h3>
              和好友继续 <b aria-hidden="true">↗</b>
            </h3>
            <p>添加聊得来的人，把话题延伸到私聊。</p>
          </Link>
          <Link to="/home/posts">
            <span>03 / POSTS</span>
            <h3>
              把想法留下 <b aria-hidden="true">↗</b>
            </h3>
            <p>发布帖子，让讨论在聊天结束后继续。</p>
          </Link>
        </div>
      </section>

      <section className="film-final" id="enter" aria-labelledby="final-title">
        <h2 id="final-title">
          故事从作品开始。
          <br />
          对话，<span>由你继续。</span>
        </h2>
        <div>
          <Link className="film-cta" to="/home/rooms">
            进入聊天室 <span aria-hidden="true">↗</span>
          </Link>
          <a href={REPO} target="_blank" rel="noreferrer">
            探索 GitHub ↗
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
