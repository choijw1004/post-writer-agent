import { useState } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import TokenPanel from './TokenPanel'

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <button
      type="button"
      onClick={copy}
      className="rounded-xl border border-line px-4 py-2 text-[14px] font-medium transition-all duration-200 hover:border-ink-sub/40 hover:bg-surface active:scale-[0.97]"
    >
      {copied ? '복사됨' : '마크다운 복사'}
    </button>
  )
}

// 이 화면의 할 일은 하나다. 읽고, 복사한다.
// 검토 결과를 나란히 두지 않는 이유: 정작 읽어야 할 초안이 좁은 컬럼에
// 갇히고, 아직 읽지도 않은 글에 대한 지적을 먼저 보게 된다.
// 다듬기가 필요하면 아래 버튼으로 넘어간다.
export default function ResultView({ result, model, onRestart, onReview }) {
  const { draft_markdown: draft, usage } = result

  return (
    <div className="step-in mx-auto w-full max-w-[760px] px-6 pt-16 pb-24">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-[26px] font-bold tracking-[-0.02em]">초안이 나왔습니다</h1>
        <div className="flex gap-2">
          <CopyButton text={draft} />
          <button
            type="button"
            onClick={onRestart}
            className="rounded-xl px-4 py-2 text-[14px] font-medium text-ink-sub transition-colors duration-200 hover:text-ink"
          >
            새로 쓰기
          </button>
        </div>
      </div>

      <article className="mt-10 rounded-2xl border border-line p-8">
        <div className="prose-blog">
          <Markdown remarkPlugins={[remarkGfm]}>{draft}</Markdown>
        </div>
      </article>

      {/* 복사해서 다시 붙여넣게 하지 않는다. 이 초안을 그대로 넘긴다. */}
      <button
        type="button"
        onClick={() => onReview(draft)}
        className="mt-6 w-full rounded-2xl border border-line px-6 py-5 text-left transition-all duration-200 hover:border-brand hover:bg-brand-soft active:scale-[0.99]"
      >
        <span className="block text-[16px] font-semibold">이 초안 다듬기</span>
        <span className="mt-1 block text-[13px] text-ink-sub">
          오타와 논리 문제를 짚어봅니다
        </span>
      </button>

      <div className="mt-6">
        <TokenPanel usage={usage} model={model} />
      </div>
    </div>
  )
}
