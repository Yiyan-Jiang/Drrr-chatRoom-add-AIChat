/** 介绍 DOLLARS 聊天室的项目灵感与主要体验。 */
import { Link } from 'react-router-dom'
import dollarsLogo from '@/assets/icon/Logo/logo.png'
import './SettingsPage.css'

/** 展示项目来历与聊天室体验。 */
export default function SettingsPage() {
  return (
    <main className="settings-origin h-full min-h-0 overflow-auto bg-black text-zinc-100">
      <div className="settings-origin__inner mx-auto w-full max-w-5xl px-5 py-8 sm:px-8 sm:py-12">
        <header className="settings-origin__hero">
          <div className="settings-origin__brand-row">
            <img
              className="settings-origin__logo"
              src={dollarsLogo}
              alt="DOLLARS 标志"
            />
            <p className="settings-origin__eyebrow">DOLLARS / PROJECT NOTE</p>
          </div>
          <div className="settings-origin__hero-copy">
            <p className="settings-origin__chapter">设定 · 01 / 项目来历</p>
            <h1>从一间聊天室的想象开始</h1>
            <p className="settings-origin__lead">
              受《无头骑士异闻录》中的 DOLLARS
              聊天室启发，尝试把那种在网络空间相遇的氛围，变成一个可以实际使用的网页聊天室。
            </p>
          </div>
          <div className="settings-origin__hero-note" aria-hidden="true">
            <span>ROOM</span>
            <span>—</span>
            <span>PEOPLE</span>
            <span>—</span>
            <span>STORIES</span>
          </div>
        </header>

        <section className="settings-origin__manifesto" aria-label="项目介绍">
          <p className="settings-origin__section-label">
            <span>01</span> 一种聊天室的气氛
          </p>
          <p className="settings-origin__manifesto-copy">
            深色界面、角色头像与聊天气泡，构成这个空间最初的轮廓。人们可以创建或加入房间，与在线成员交流；也可以添加好友私聊，或用帖子把一段想法留下来。
          </p>
        </section>

        <section
          className="settings-origin__chapters"
          aria-label="项目的三个侧面"
        >
          <article className="settings-origin__chapter-card">
            <p className="settings-origin__card-index">02 / THE ROOM</p>
            <h2>进入一个房间</h2>
            <p>
              创建房间、设置简介与标签，或加入已有的聊天。消息实时抵达，房间成员也能彼此看见。
            </p>
            <Link className="settings-origin__text-link" to="/home/rooms">
              浏览聊天室 <span aria-hidden="true">↗</span>
            </Link>
          </article>
          <article className="settings-origin__chapter-card">
            <p className="settings-origin__card-index">03 / THE PEOPLE</p>
            <h2>让相遇继续</h2>
            <p>
              添加好友，开始一对一交流；好友动态让房间之外的分享，也有机会被看见。
            </p>
            <Link className="settings-origin__text-link" to="/friends">
              查看好友动态 <span aria-hidden="true">↗</span>
            </Link>
          </article>
          <article className="settings-origin__chapter-card">
            <p className="settings-origin__card-index">04 / THE STORIES</p>
            <h2>把想法留下来</h2>
            <p>
              发布帖子、评论并参与互动。聊天室里的交流，也可以延伸成更完整的表达。
            </p>
            <Link className="settings-origin__text-link" to="/home/posts">
              浏览帖子 <span aria-hidden="true">↗</span>
            </Link>
          </article>
        </section>

        <section className="settings-origin__project-note">
          <div>
            <p className="settings-origin__section-label">
              <span>05</span> 一个个人 IO 练习项目
            </p>
            <p className="settings-origin__project-copy">
              前端使用 React 与 TypeScript，后端使用 FastAPI 与
              Socket.IO，业务数据存储在 MySQL。
            </p>
          </div>
          <p className="settings-origin__history-note">
            仓库名称保留了历史上的 <code>AIChat</code>；当前版本已移除 AI 功能。
          </p>
        </section>

        <section className="settings-origin__invitation">
          <p className="settings-origin__invitation-mark" aria-hidden="true">
            D
          </p>
          <div>
            <p className="settings-origin__section-label">你的下一步</p>
            <h2>找到一个房间，开始一段对话。</h2>
          </div>
          <Link className="settings-origin__primary-link" to="/home/rooms">
            进入聊天室 <span aria-hidden="true">→</span>
          </Link>
        </section>

        <footer className="settings-origin__footer">
          <p>账号资料与当前登录管理</p>
          <Link to="/my">
            前往我的页面 <span aria-hidden="true">↗</span>
          </Link>
        </footer>
      </div>
    </main>
  )
}
