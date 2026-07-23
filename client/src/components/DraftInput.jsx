import { useRef } from 'react'

// 다듬을 글을 받는다. 붙여넣기와 .md 열기 둘 다 연다.
// 초안 작성에서 넘어온 경우에는 이미 채워진 채로 들어온다.
export default function DraftInput({ value, onChange }) {
  const inputRef = useRef(null)

  async function handleFile(event) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    onChange(await file.text())
  }

  const chars = value.length

  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="다듬을 글을 붙여넣으세요. 마크다운 그대로 넣으면 됩니다."
        rows={12}
        className="w-full resize-y rounded-2xl border border-line bg-surface px-5 py-4 text-[15px] leading-[1.7] transition-all duration-200 outline-none placeholder:text-ink-sub focus:border-brand focus:bg-white"
      />

      <div className="mt-3 flex items-center justify-between">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="rounded-xl border border-line px-4 py-2 text-[14px] font-medium transition-all duration-200 hover:border-ink-sub/40 hover:bg-surface active:scale-[0.97]"
        >
          .md 파일 열기
        </button>
        <span className="text-[13px] text-ink-sub">
          {chars > 0 ? `${chars.toLocaleString()}자` : ''}
        </span>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".md,.markdown,text/markdown"
        className="hidden"
        onChange={handleFile}
      />
    </div>
  )
}
