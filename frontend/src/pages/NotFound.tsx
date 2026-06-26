import { Link, useNavigate } from 'react-router-dom'
import logoSource from '@/assets/icon/Logo/logo.png'
import backImg from '@/assets/pages/404/backImg.png'
import backIconModle from '@/assets/pages/404/backIconModle.png'

function HomeIcon() {
  return (
    <svg aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        d="m3 11 9-8 9 8"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
      <path
        d="M5 10v10h14V10"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
      <path
        d="M10 20v-6h4v6"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
    </svg>
  )
}

function BackIcon() {
  return (
    <svg aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        d="M10 19 3 12m0 0 7-7m-7 7h18"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
    </svg>
  )
}

export default function NotFound() {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/gate')
  }

  const handleGoBack = () => {
    if (window.history.length > 1) {
      navigate(-1)
      return
    }

    navigate('/gate')
  }

  return (
    <div className="min-h-screen bg-[#090909] text-white">
      <header className="fixed inset-x-0 top-0 z-40 border-b border-zinc-900 bg-black/95">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link className="flex min-w-0 items-center gap-3" to="/">
            <img alt="Drrr logo" className="h-8 w-8 shrink-0 object-contain" src={logoSource} />
            <span className="truncate text-sm font-semibold text-zinc-100">404</span>
          </Link>
          <Link className="text-sm text-zinc-400 transition hover:text-zinc-100" to="/gate">
            返回入口
          </Link>
        </div>
      </header>

      <main className="pt-14">
        <div
          className="relative min-h-[calc(100vh-3.5rem)] w-full bg-cover bg-center bg-no-repeat before:pointer-events-none before:absolute before:inset-0 before:bg-black/60 before:content-['']"
          style={{ backgroundImage: `url(${backImg})` }}
        >
          <section className="absolute left-[10%] top-[18%] z-10 flex w-[min(82vw,30rem)] flex-col items-center gap-3 text-center text-white md:left-35 md:top-35">
            <h1 className="text-8xl font-bold leading-none sm:text-9xl">404</h1>
            <h2 className="text-2xl font-semibold">页面未找到</h2>
            <p className="max-w-sm leading-7 text-zinc-200">
              您尝试访问的页面可能不存在或已被删除。请确认 URL 后再尝试。
            </p>

            <div className="mt-5 flex w-60 flex-col gap-2 border-t border-white/40 pt-3 text-white items-center">
              <button
                className="inline-flex h-9 w-56 items-center justify-center gap-2 rounded border border-white/60 px-3 text-sm transition hover:bg-white hover:text-black cursor-pointer"
                onClick={handleGoHome}
                type="button"
              >
                <HomeIcon />
                返回首页
              </button>
              <button
                className="inline-flex h-9 w-56 items-center justify-center gap-2 rounded border border-white/30 px-3 text-sm transition hover:border-white/60 hover:bg-white/10 cursor-pointer"
                onClick={handleGoBack}
                type="button"
              >
                <BackIcon />
                返回上一页
              </button>
            </div>
          </section>

          <section className='absolute right-[31%] z-10 hidden h-40 w-55 md:top-20 xl:block'>
            <svg
              aria-hidden="true"
              className="absolute inset-0 h-full w-full text-white/65"
              fill="none"
              viewBox="0 0 220 160"
            >
              <path
                d="M14 10H194C201.732 10 208 16.268 208 24V102C208 109.732 201.732 116 194 116H154L172 132L148 116H14C6.268 116 0 109.732 0 102V24C0 16.268 6.268 10 14 10Z"
                stroke="currentColor"
                strokeDasharray="2.5 3.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.1"
              />
            </svg>
            <div className="relative z-10 flex h-full flex-col px-6 py-5 text-left text-sm leading-6 text-white">
              <div className="max-w-40">
                您要找的页面似乎在某处消失了......
              </div>
              <img src={backIconModle} alt="卫图" className='mt-1 h-9 w-9  self-center'/>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
