import { useState, type FormEvent } from 'react'
import { PostsMarkdownRenderer } from '@/features/posts/markdownRenderer'

type PostEditorProps = {
  disabled?: boolean
  onSubmit: (payload: { title: string; content: string }) => Promise<unknown>
}

export default function PostEditor({ disabled = false, onSubmit }: PostEditorProps) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [mode, setMode] = useState<'write' | 'preview'>('write')
  const [error, setError] = useState('')

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const nextTitle = title.trim()
    const nextContent = content.trim()
    if (!nextTitle || !nextContent) {
      setError('标题和正文都不能为空。')
      return
    }
    setError('')
    try {
      await onSubmit({ title: nextTitle, content: nextContent })
      setTitle('')
      setContent('')
      setMode('write')
      setOpen(false)
    } catch {
      setError('发布失败，请稍后重试。')
    }
  }

  return (
    <div className="absolute bottom-4 right-4 z-20 flex flex-col items-end gap-3">
      {open ? (
        <form
          className="w-[min(92vw,420px)] border border-white bg-[#090909] p-5 text-white shadow-2xl"
          onSubmit={handleSubmit}
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-bold">发布帖子</h2>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="h-7 w-7 rounded-full border border-white text-sm leading-6 hover:bg-white hover:text-black"
              aria-label="关闭发帖表单"
            >
              ×
            </button>
          </div>

          <div className="flex flex-col gap-3">
            <input
              className="h-9 rounded-sm border border-white bg-black px-3 text-sm text-white outline-none placeholder:text-zinc-600 disabled:opacity-60"
              maxLength={80}
              placeholder="标题"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={disabled}
            />

            <div className="flex w-fit rounded-sm border border-zinc-700 p-0.5 text-xs">
              <button
                className={`px-3 py-1 ${mode === 'write' ? 'bg-white text-black' : 'text-zinc-300'}`}
                type="button"
                onClick={() => setMode('write')}
              >
                编辑
              </button>
              <button
                className={`px-3 py-1 ${mode === 'preview' ? 'bg-white text-black' : 'text-zinc-300'}`}
                type="button"
                onClick={() => setMode('preview')}
              >
                预览
              </button>
            </div>

            {mode === 'write' ? (
              <textarea
                className="min-h-52 resize-y rounded-sm border border-white bg-black px-3 py-2 text-sm leading-6 text-white outline-none placeholder:text-zinc-600 disabled:opacity-60"
                maxLength={20000}
                placeholder="支持 Markdown"
                value={content}
                onChange={(event) => setContent(event.target.value)}
                disabled={disabled}
              />
            ) : (
              <div className="min-h-52 max-h-80 overflow-auto rounded-sm border border-white bg-black px-3 py-2">
                {content.trim() ? (
                  <PostsMarkdownRenderer markdown={content} />
                ) : (
                  <p className="text-sm text-zinc-600">暂无预览内容。</p>
                )}
              </div>
            )}

            {error && <p className="text-sm text-red-300">{error}</p>}

            <button
              className="h-9 w-full rounded-md border border-white bg-white font-semibold text-black transition hover:bg-gray-200 disabled:opacity-60"
              type="submit"
              disabled={disabled}
            >
              {disabled ? '发布中...' : '发布'}
            </button>
          </div>
        </form>
      ) : null}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex h-12 w-12 items-center justify-center rounded-full border border-white bg-pink-100 text-2xl font-bold text-black shadow-lg transition hover:scale-105"
        aria-label={open ? '关闭发帖表单' : '打开发帖表单'}
      >
        {open ? '×' : '+'}
      </button>
    </div>
  )
}
