/** 提供独立的桌面 Markdown 发帖页面、实时预览和局部目录。 */
import {
  useDeferredValue,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react'
import { isAxiosError, type AxiosError } from 'axios'
import {
  Link,
  useBeforeUnload,
  useBlocker,
  useNavigate,
} from 'react-router-dom'
import logoSource from '@/assets/icon/Logo/logo.png'
import { postsApi } from '@/api'
import PostMarkdownArticle from '@/features/posts/PostMarkdownArticle'

const TITLE_MAX_LENGTH = 80
const CONTENT_MAX_LENGTH = 20000

/** 预览中一个真实二级或三级标题的目录信息。 */
type ComposeHeading = {
  /** 预览 DOM 中的唯一锚点。 */
  id: string
  /** 标题层级。 */
  level: 2 | 3
  /** 标题实际渲染出的文本。 */
  text: string
}

/** 将发布请求错误转换为可以直接显示给用户的说明。 */
function getPublishError(error: AxiosError): string {
  if (!error.response) {
    return '网络连接失败，请检查网络后重试。'
  }

  if (error.response.status === 400 || error.response.status === 422) {
    return '标题或正文不符合要求，请检查后重试。'
  }

  if (error.response.status === 401) {
    return '登录状态已失效，请重新登录。'
  }

  if (error.response.status >= 500) {
    return '服务器暂时无法处理请求，请稍后重试。'
  }

  return '发布失败，请稍后重试。'
}

/** 展示独立发帖页的品牌栏。 */
function ComposeHeader() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-900 bg-black px-4 text-zinc-100 sm:px-6">
      <Link className="flex min-w-0 items-center gap-3" to="/home/posts">
        <img
          alt="Drrr logo"
          className="h-8 w-8 shrink-0 object-contain"
          src={logoSource}
        />
        <span className="truncate text-sm font-semibold">发布帖子</span>
      </Link>
      <nav className="flex items-center gap-4 text-sm">
        <Link
          className="text-zinc-400 transition hover:text-zinc-100"
          to="/home/posts"
        >
          帖子
        </Link>
        <Link
          className="text-zinc-400 transition hover:text-zinc-100"
          to="/home/rooms"
        >
          聊天室
        </Link>
      </nav>
    </header>
  )
}

/** 提供实时 Markdown 预览、实际标题目录和局部目录滚动。 */
function ComposePreview({ markdown }: { markdown: string }) {
  const previewScrollRef = useRef<HTMLDivElement>(null)
  const [headings, setHeadings] = useState<ComposeHeading[]>([])

  useEffect(() => {
    const previewRoot = previewScrollRef.current
    if (!previewRoot) {
      return
    }

    const updateHeadings = () => {
      const elements = Array.from(
        previewRoot.querySelectorAll<HTMLElement>('h2, h3'),
      )
      const nextHeadings = elements.map((element, index) => {
        const id = `post-compose-heading-${index}`
        if (element.id !== id) {
          element.id = id
        }
        return {
          id,
          level: element.tagName === 'H2' ? (2 as const) : (3 as const),
          text: element.textContent?.trim() ?? '',
        }
      })

      setHeadings((current) => {
        const currentSignature = current
          .map((heading) => `${heading.id}:${heading.level}:${heading.text}`)
          .join('|')
        const nextSignature = nextHeadings
          .map((heading) => `${heading.id}:${heading.level}:${heading.text}`)
          .join('|')
        return currentSignature === nextSignature ? current : nextHeadings
      })
    }

    const observer = new MutationObserver(updateHeadings)
    observer.observe(previewRoot, {
      childList: true,
      characterData: true,
      subtree: true,
    })
    updateHeadings()

    return () => observer.disconnect()
  }, [markdown])

  const handleNavigate = (id: string) => {
    const previewRoot = previewScrollRef.current
    const heading = document.getElementById(id)
    if (!previewRoot || !heading || !previewRoot.contains(heading)) {
      return
    }

    const rootRect = previewRoot.getBoundingClientRect()
    const headingRect = heading.getBoundingClientRect()
    previewRoot.scrollTo({
      top: previewRoot.scrollTop + headingRect.top - rootRect.top - 20,
      behavior: 'smooth',
    })
  }

  return (
    <div className="grid min-h-0 min-w-0 flex-1 grid-cols-[minmax(0,1fr)_150px] gap-4">
      <div
        ref={previewScrollRef}
        className="min-h-0 min-w-0 overflow-y-auto rounded-lg border border-[#e2e2e3] bg-white px-5 py-5 sm:px-7"
        aria-label="Markdown 预览"
      >
        {markdown.trim() ? (
          <PostMarkdownArticle markdown={markdown} />
        ) : (
          <p className="text-sm leading-7 text-[#67676c]">
            输入 Markdown 后将在这里预览。
          </p>
        )}
      </div>

      <aside className="flex min-h-0 min-w-0 flex-col rounded-lg border border-[#e2e2e3] bg-white p-3">
        <p className="shrink-0 text-xs font-semibold uppercase tracking-[0.16em] text-[#67676c]">
          目录
        </p>
        <div className="mt-2 min-h-0 overflow-y-auto">
          {headings.length > 0 ? (
            <nav aria-label="正文目录" className="flex flex-col gap-1">
              {headings.map((heading) => (
                <button
                  className={`min-w-0 border-l border-transparent py-1 text-left text-sm leading-6 text-[#3c3c43] transition hover:border-[#3451b2] hover:text-[#3451b2] ${heading.level === 3 ? 'pl-4' : 'pl-1'}`}
                  key={heading.id}
                  type="button"
                  title={heading.text}
                  onClick={() => handleNavigate(heading.id)}
                >
                  <span className="block truncate whitespace-nowrap">
                    {heading.text}
                  </span>
                </button>
              ))}
            </nav>
          ) : (
            <p className="text-xs leading-5 text-[#99999f]">暂无目录</p>
          )}
        </div>
      </aside>
    </div>
  )
}

/** 独立桌面 Markdown 发帖页，负责输入、发布和离开确认。 */
export default function PostCompose() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [allowNavigation, setAllowNavigation] = useState(false)
  const deferredContent = useDeferredValue(content.trim())
  const isDirty = !allowNavigation && Boolean(title.trim() || content.trim())
  const isDirtyRef = useRef(false)
  const isActiveRef = useRef(true)
  const leaveDialogRef = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    isActiveRef.current = true
    return () => {
      isActiveRef.current = false
    }
  }, [])
  useEffect(() => {
    isDirtyRef.current = isDirty
  }, [isDirty])
  const blocker = useBlocker(() => isDirtyRef.current)

  useEffect(() => {
    const dialog = leaveDialogRef.current
    if (!dialog) {
      return
    }

    if (blocker.state === 'blocked') {
      if (!dialog.open) {
        dialog.showModal()
      }
      return
    }

    if (dialog.open) {
      dialog.close()
    }
  }, [blocker.state])

  useBeforeUnload((event) => {
    if (isDirty) {
      event.preventDefault()
    }
  })

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const nextTitle = title.trim()
    const nextContent = content.trim()
    if (!nextTitle || !nextContent) {
      setErrorMessage('标题和正文都不能为空。')
      return
    }

    setErrorMessage('')
    setIsSubmitting(true)
    try {
      const created = await postsApi.create({
        title: nextTitle,
        content: nextContent,
      })
      if (!isActiveRef.current) {
        return
      }
      isDirtyRef.current = false
      setAllowNavigation(true)
      navigate(`/posts/${created.id}`)
    } catch (error: unknown) {
      if (!isAxiosError(error)) {
        throw error
      }
      if (!isActiveRef.current) {
        return
      }
      setErrorMessage(getPublishError(error))
    } finally {
      if (isActiveRef.current) {
        setIsSubmitting(false)
      }
    }
  }

  return (
    <main className="flex h-screen min-h-0 flex-col bg-[#f6f6f7] text-[#213547]">
      <ComposeHeader />

      <form
        id="post-compose-form"
        className="flex min-h-0 flex-1 flex-col gap-4 px-4 py-5 pb-24 sm:px-6"
        onSubmit={handleSubmit}
      >
        <div className="mx-auto flex w-full max-w-7xl shrink-0 flex-col gap-2">
          <label
            className="text-sm font-semibold text-[#213547]"
            htmlFor="post-compose-title"
          >
            标题
          </label>
          <input
            id="post-compose-title"
            className="h-11 rounded-lg border border-[#dcdfe6] bg-white px-3 text-base text-[#213547] outline-none transition placeholder:text-[#99999f] focus:border-[#3451b2] focus:ring-2 focus:ring-[#dfe3ff] disabled:opacity-60"
            maxLength={TITLE_MAX_LENGTH}
            placeholder="输入帖子标题"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            disabled={isSubmitting}
          />
        </div>

        <div className="mx-auto grid min-h-0 w-full max-w-7xl flex-1 grid-cols-[minmax(0,45fr)_minmax(0,55fr)] gap-4">
          <section className="flex min-h-0 min-w-0 flex-col gap-2">
            <label
              className="shrink-0 text-sm font-semibold text-[#213547]"
              htmlFor="post-compose-content"
            >
              Markdown 正文
            </label>
            <textarea
              id="post-compose-content"
              className="min-h-0 min-w-0 flex-1 resize-none overflow-y-auto rounded-lg border border-[#dcdfe6] bg-white p-4 font-mono text-sm leading-6 text-[#213547] outline-none transition placeholder:text-[#99999f] focus:border-[#3451b2] focus:ring-2 focus:ring-[#dfe3ff] disabled:opacity-60"
              maxLength={CONTENT_MAX_LENGTH}
              placeholder="支持 Markdown 语法"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              disabled={isSubmitting}
            />
            <p className="shrink-0 text-right text-xs text-[#67676c]">
              {content.length}/{CONTENT_MAX_LENGTH}
            </p>
          </section>

          <section className="flex min-h-0 min-w-0 flex-col gap-2">
            <h2 className="shrink-0 text-sm font-semibold text-[#213547]">
              预览
            </h2>
            <ComposePreview markdown={deferredContent} />
          </section>
        </div>
      </form>

      <footer className="fixed inset-x-0 bottom-0 z-30 border-t border-[#dcdfe6] bg-[#f6f6f7]/95 px-4 py-3 backdrop-blur sm:px-6">
        <div className="mx-auto flex min-h-10 w-full max-w-7xl items-center justify-end gap-4">
          {errorMessage && (
            <p className="mr-auto text-sm text-red-700" role="alert">
              {errorMessage}
            </p>
          )}
          <button
            className="h-10 shrink-0 rounded-lg bg-black px-6 text-sm font-semibold text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
            type="submit"
            form="post-compose-form"
            disabled={isSubmitting}
          >
            {isSubmitting ? '发布中...' : '发布'}
          </button>
        </div>
      </footer>

      <dialog
        ref={leaveDialogRef}
        aria-labelledby="post-compose-leave-title"
        className="m-auto w-[min(100%-2rem,24rem)] rounded-lg border border-[#dcdfe6] bg-white p-5 text-[#213547] shadow-2xl backdrop:bg-black/40"
        onCancel={(event) => {
          event.preventDefault()
          blocker.reset?.()
        }}
      >
        <h2 id="post-compose-leave-title" className="text-base font-semibold">
          放弃未发布内容？
        </h2>
        <p className="mt-2 text-sm leading-6 text-[#67676c]">
          当前标题或正文尚未发布。离开后这些内容不会保存。
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button
            className="rounded border border-[#dcdfe6] px-3 py-2 text-sm text-[#3c3c43] transition hover:bg-[#f6f6f7]"
            type="button"
            onClick={() => blocker.reset?.()}
          >
            继续编辑
          </button>
          <button
            className="rounded bg-black px-3 py-2 text-sm font-semibold text-white transition hover:bg-zinc-800"
            type="button"
            onClick={() => {
              isActiveRef.current = false
              isDirtyRef.current = false
              setAllowNavigation(true)
              blocker.proceed?.()
            }}
          >
            离开页面
          </button>
        </div>
      </dialog>
    </main>
  )
}
