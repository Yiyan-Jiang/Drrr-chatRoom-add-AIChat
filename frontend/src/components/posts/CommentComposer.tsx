type CommentComposerProps = {
  value: string
  disabled?: boolean
  onChange: (value: string) => void
  onSubmit: () => Promise<void>
}

export default function CommentComposer({
  value,
  disabled = false,
  onChange,
  onSubmit,
}: CommentComposerProps) {
  return (
    <div className="rounded-lg border border-[#e2e2e3] bg-white p-4 shadow-sm">
      <textarea
        className="min-h-24 w-full resize-y rounded border border-[#e2e2e3] bg-white px-3 py-2 text-sm leading-6 text-[#213547] outline-none transition placeholder:text-[#a8a8ad] focus:border-[#3451b2]"
        maxLength={3000}
        placeholder="写下评论"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      />
      <button
        className="mt-3 rounded border border-[#3451b2] px-4 py-2 text-sm font-medium text-[#3451b2] transition hover:bg-[#f1f3ff] disabled:cursor-not-allowed disabled:opacity-50"
        type="button"
        disabled={disabled || !value.trim()}
        onClick={() => void onSubmit()}
      >
        评论
      </button>
    </div>
  )
}
