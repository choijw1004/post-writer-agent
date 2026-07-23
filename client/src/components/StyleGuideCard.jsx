// 문체 분석 결과. 작가가 글을 다 쓸 때까지 기다리지 않고, 분석 단계가
// 끝나는 즉시 뜬다. "기존 글에서 무엇을 읽어냈는가"를 보여주는 자리라
// 이 앱의 데모 포인트다.
const ROWS = [
  ['어투', 'tone'],
  ['문장 종결', 'sentence_ending'],
  ['소제목', 'heading_style'],
  ['코드 예시', 'code_example_ratio'],
  ['전개 구조', 'structure_pattern'],
  ['어휘·표현', 'vocabulary'],
]

export default function StyleGuideCard({ styleGuide, sampleTitles }) {
  if (!styleGuide) return null

  return (
    <div className="step-in rounded-2xl border border-line bg-surface p-6">
      <p className="text-[13px] font-medium text-ink-sub">기존 글에서 읽어낸 문체</p>

      <dl className="mt-5 space-y-4">
        {ROWS.map(([label, key]) =>
          styleGuide[key] ? (
            <div key={key} className="flex gap-4">
              <dt className="w-20 shrink-0 text-[14px] text-ink-sub">{label}</dt>
              <dd className="flex-1 text-[14px] leading-[1.6] font-medium">
                {styleGuide[key]}
              </dd>
            </div>
          ) : null,
        )}
        <div className="flex gap-4">
          <dt className="w-20 shrink-0 text-[14px] text-ink-sub">문단 길이</dt>
          <dd className="flex-1 text-[14px] font-medium">
            평균 {styleGuide.avg_paragraph_sentences}문장
          </dd>
        </div>
      </dl>

      {styleGuide.dos?.length > 0 && (
        <div className="mt-6 border-t border-line pt-5">
          <p className="text-[13px] font-medium text-ink-sub">지킬 것</p>
          <ul className="mt-2 space-y-1.5">
            {styleGuide.dos.map((item) => (
              <li key={item} className="text-[14px] leading-[1.6]">
                · {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {sampleTitles?.length > 0 && (
        <p className="mt-6 border-t border-line pt-5 text-[13px] text-ink-sub">
          참고한 글 {sampleTitles.length}편: {sampleTitles.join(', ')}
        </p>
      )}
    </div>
  )
}
