// 지적 목록.
//
// source 로 무게를 가른다. 'auto' 는 코드가 확정한 것이고 'model' 은 모델의
// 판단이다. 둘을 같은 모양으로 나열하면 읽는 사람이 전부 의심하거나 전부
// 믿게 되므로, 배지로 구분하고 확실한 것을 위에 둔다.
const BADGE = {
  auto: {
    label: '자동 검사',
    className: 'bg-[#48664d]/10 text-[#48664d]',
  },
  model: {
    label: '모델 판단',
    className: 'bg-surface text-ink-sub',
  },
}

function Note({ note, index }) {
  const badge = BADGE[note.source] ?? BADGE.model

  return (
    <li className="border-t border-line pt-6 first:border-0 first:pt-0">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[13px] text-ink-sub">{index}</span>
        <span
          className={`rounded-md px-2 py-0.5 text-[12px] font-medium ${badge.className}`}
        >
          {badge.label}
        </span>
        <span className="rounded-md bg-surface px-2 py-0.5 text-[12px] text-ink-sub">
          {note.kind}
        </span>
      </div>

      <p className="mt-3 text-[13px] font-medium text-ink-sub">{note.location}</p>
      <p className="mt-1.5 text-[15px] leading-[1.6]">{note.problem}</p>
      <p className="mt-2.5 rounded-xl bg-surface px-4 py-3 text-[14px] leading-[1.6] text-ink-sub">
        {note.suggestion}
      </p>
    </li>
  )
}

export default function ReviewNotes({ result }) {
  const { notes, auto_count: autoCount, model_count: modelCount, overall } = result

  if (notes.length === 0) {
    return (
      <div className="rounded-2xl border border-line p-8 text-center">
        <p className="text-[16px] font-semibold">짚을 곳이 없습니다</p>
        {overall && (
          <p className="mt-2 text-[14px] leading-[1.6] text-ink-sub">{overall}</p>
        )}
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <p className="text-[15px] font-bold">{notes.length}건을 짚었습니다</p>
        <p className="text-[13px] text-ink-sub">
          자동 검사 {autoCount}건 · 모델 판단 {modelCount}건
        </p>
      </div>

      <p className="mt-2 text-[13px] leading-[1.6] text-ink-sub">
        글을 대신 고치지 않습니다. 자동 검사는 코드가 확정한 것이고, 모델 판단은
        참고용입니다. 반영 여부는 직접 정하세요.
      </p>

      <ol className="mt-8 space-y-6">
        {notes.map((note, i) => (
          <Note key={`${note.location}-${i}`} note={note} index={i + 1} />
        ))}
      </ol>

      {overall && (
        <p className="mt-8 border-t border-line pt-6 text-[14px] leading-[1.6] text-ink-sub">
          {overall}
        </p>
      )}
    </div>
  )
}
