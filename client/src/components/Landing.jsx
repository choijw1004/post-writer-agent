// 두 갈래로 나눈 이유: 사용자가 이 도구를 찾는 시점이 다르다.
// 아직 안 쓴 사람과 이미 써둔 사람은 필요한 게 서로 다르고, 후자에게
// "먼저 초안을 생성하세요"라고 요구할 이유가 없다.
const ENTRIES = [
  {
    key: 'draft',
    title: '초안 작성',
    body: '기존 글에서 문체를 뽑아내 새 글의 초안을 씁니다.',
    hint: '마크다운 폴더 또는 velog',
  },
  {
    key: 'review',
    title: '글 다듬기',
    body: '이미 써둔 글에서 오타와 논리 문제를 찾아 짚어줍니다.',
    hint: '고쳐주지 않고 짚어만 줍니다',
  },
]

export default function Landing({ onStart }) {
  return (
    <div className="step-in mx-auto w-full max-w-[560px] px-6 pt-24 pb-24">
      <div className="flex items-center gap-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-brand" />
        <span className="text-[15px] font-bold tracking-[-0.01em]">초록</span>
        <span className="text-[13px] text-ink-sub">cholog</span>
      </div>

      <h1 className="mt-12 text-[34px] leading-[1.3] font-bold tracking-[-0.03em]">
        내 문체 그대로,
        <br />
        다음 글의 초안까지
      </h1>

      <p className="mt-5 text-[16px] leading-[1.65] text-ink-sub">
        초록(抄錄)은 요점을 뽑아 적는다는 뜻입니다. 글에서 문체를 뽑아 적어두고,
        그 문체로 새 글을 씁니다.
      </p>

      <div className="mt-12 space-y-4">
        {ENTRIES.map(({ key, title, body, hint }) => (
          <button
            key={key}
            type="button"
            onClick={() => onStart(key)}
            className="w-full rounded-2xl border border-line bg-white px-6 py-7 text-left transition-all duration-200 hover:border-brand hover:bg-brand-soft active:scale-[0.99]"
          >
            <span className="block text-[19px] font-bold tracking-[-0.01em]">
              {title}
            </span>
            <span className="mt-2 block text-[15px] leading-[1.6] text-ink-sub">
              {body}
            </span>
            <span className="mt-3 block text-[13px] text-ink-sub">{hint}</span>
          </button>
        ))}
      </div>

      <p className="mt-16 border-t border-line pt-8 text-[13px] leading-[1.7] text-ink-sub">
        글을 통째로 모델에 밀어 넣지 않습니다. 문체를 규칙으로 압축해 넘기기
        때문에 참고할 글이 많아져도 비용이 그만큼 늘지 않습니다. 단계별로 쓴
        토큰은 결과 화면에서 확인할 수 있습니다.
      </p>
    </div>
  )
}
