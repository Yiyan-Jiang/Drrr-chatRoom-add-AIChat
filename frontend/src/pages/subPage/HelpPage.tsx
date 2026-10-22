/** 提供主要功能的操作说明与站内入口。 */
import { Link } from 'react-router-dom'

/** 展示聊天室、好友、私聊和帖子的使用说明。 */
export default function HelpPage() {
  return (
    <div className="h-full overflow-auto bg-black px-4 py-7 text-zinc-100 sm:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-2xl font-semibold">帮助</h1>
        <p className="mt-2 text-sm text-zinc-400">
          从这里了解 DOLLARS 的主要功能。
        </p>
        <div className="mt-6 space-y-4">
          <section className="rounded-sm border border-zinc-700 p-5">
            <h2 className="font-semibold">聊天室</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-300">
              在聊天室列表中选择房间并加入。进入房间后，在消息输入框中填写内容并发送，与房间成员交流。
            </p>
            <Link
              to="/home/rooms"
              className="mt-3 inline-block text-sm underline underline-offset-4 hover:text-zinc-300"
            >
              浏览聊天室
            </Link>
          </section>
          <section className="rounded-sm border border-zinc-700 p-5">
            <h2 className="font-semibold">好友与申请</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-300">
              在好友管理页面输入完整用户名，点击“查找用户”，确认结果后点击“发送好友申请”。也可以点击聊天室或帖子中的用户头像发起申请。在好友管理页面接受或拒绝收到的申请，也可以取消尚未处理的已发申请。好友动态会显示好友最近发布的帖子。
            </p>
            <Link
              to="/friends/manage"
              className="mt-3 inline-block text-sm underline underline-offset-4 hover:text-zinc-300"
            >
              管理好友与申请
            </Link>
            <Link
              to="/friends"
              className="ml-5 mt-3 inline-block text-sm underline underline-offset-4 hover:text-zinc-300"
            >
              查看好友动态
            </Link>
          </section>
          <section className="rounded-sm border border-zinc-700 p-5">
            <h2 className="font-semibold">私聊</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-300">
              在好友管理页面点击“私聊”开始交流。私聊需要双方保持好友关系，退出私聊后可以回到好友管理页面。
            </p>
            <Link
              to="/friends/manage"
              className="mt-3 inline-block text-sm underline underline-offset-4 hover:text-zinc-300"
            >
              管理好友并开始私聊
            </Link>
          </section>
          <section className="rounded-sm border border-zinc-700 p-5">
            <h2 className="font-semibold">帖子与互动</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-300">
              在帖子列表浏览内容，打开帖子查看详情、评论或参与互动。你可以发布自己的帖子，并在“我的页面”查看发布、评论、收藏和喜欢的内容。
            </p>
            <div className="mt-3 flex flex-wrap gap-5 text-sm">
              <Link
                to="/home/posts"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                浏览帖子
              </Link>
              <Link
                to="/posts/new"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                发布帖子
              </Link>
              <Link
                to="/my"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                我的页面
              </Link>
            </div>
          </section>
          <section className="rounded-sm border border-zinc-700 p-5">
            <h2 className="font-semibold">资料与账号</h2>
            <p className="mt-3 text-sm leading-7 text-zinc-300">
              在个人资料中修改昵称、简介和内置头像，点击“保存资料”后生效。在“我的页面”退出登录或注销账号；设定页面介绍项目起源。
            </p>
            <div className="mt-3 flex gap-5 text-sm">
              <Link
                to="/profile"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                个人资料
              </Link>
              <Link
                to="/settings"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                项目起源
              </Link>
              <Link
                to="/my"
                className="underline underline-offset-4 hover:text-zinc-300"
              >
                我的页面
              </Link>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
