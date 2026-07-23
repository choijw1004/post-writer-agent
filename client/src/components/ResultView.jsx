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

// 편집자 지적. '수정 제안'이지 '수정된 원고'가 아니다.
// 무엇을 반영할지는 사람이 정한다.
function EditNotes({ report }) {
  return (
    <div className="rounded-2xl border border-line p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="text-[15px] font-bold">수정 제안</h2>
        <span className="text-[13px] text-ink-sub">{report.notes.length}건</span>
      </div>

      <p className="mt-2 text-[13px] leading-[1.6] text-ink-sub">
        원고를 대신 고치지 않고 지적만 합니다. 반영 여부는 직접 정하세요.
      </p>

      {report.notes.length === 0 ? (
        <p className="mt-6 text-[14px] text-ink-sub">지적 사항이 없습니다.</p>
      ) : (
        <ol className="mt-6 space-y-5">
          {report.notes.map((note, i) => (
            <li key={i} className="border-t border-line pt-5 first:border-0 first:pt-0">
              <p className="text-[13px] font-medium text-brand-dark">
                {note.location}
              </p>
              <p className="mt-1.5 text-[14px] leading-[1.6]">{note.problem}</p>
              <p className="mt-2 rounded-xl bg-surface px-3.5 py-2.5 text-[13px] leading-[1.6] text-ink-sub">
                {note.suggestion}
              </p>
            </li>
          ))}
        </ol>
      )}

      {report.overall && (
        <p className="mt-6 border-t border-line pt-5 text-[13px] leading-[1.6] text-ink-sub">
          {report.overall}
        </p>
      )}
    </div>
  )
}

export default function ResultView({ result, model, onRestart }) {
  const { draft_markdown: draft, edit_report: report, usage } = result

  return (
    <div className="step-in mx-auto w-full max-w-[1080px] px-6 pt-16 pb-24">
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

      {/* 초안과 지적 목록을 나란히 둔다. 좁은 화면에서는 세로로 쌓인다. */}
      <div className="mt-10 grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <article className="rounded-2xl border border-line p-8">
          <div className="prose-blog">
            <Markdown remarkPlugins={[remarkGfm]}>{draft}</Markdown>
          </div>
        </article>

        <EditNotes report={report} />
      </div>

      <div className="mt-6">
        <TokenPanel usage={usage} model={model} />
      </div>
    </div>
  )
}
