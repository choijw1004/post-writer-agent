// 두 갈래로 나눈 이유: 사용자가 이 도구를 찾는 시점이 다르다.
// 아직 안 쓴 사람과 이미 써둔 사람은 필요한 게 서로 다르고, 후자에게
// "먼저 초안을 생성하세요"라고 요구할 이유가 없다.
const ENTRIES = [
  {
    key: 'draft',
    title: '초안 작성',
    body: '기존 글과 경험을 바탕으로 새로운 기술 글의 초안을 작성합니다.',
    hint: '마크다운 폴더, velog, 아직 쓴 글이 없어도 괜찮아요',
  },
  {
    key: 'review',
    title: '퇴고',
    body: '작성한 글의 오탈자와 논리 흐름을 점검해 더 읽기 좋은 글로 다듬습니다.',
    hint: '문체는 유지하고, 부족한 설명과 어색한 연결만 보완해요.',
  },
]

export default function Landing({ onStart }) {
  return (
    <div className="step-in mx-auto w-full max-w-[560px] px-6 pt-24 pb-24">
      {/* <div className="flex items-center gap-2.5">
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: '#48664d' }} />
        <span className="text-[15px] font-bold tracking-[-0.01em]">초록</span>
        <span className="text-[13px] text-ink-sub">cholog</span>
      </div> */}

      <h1 className="mt-12 flex items-end gap-3 text-[44px] leading-[0.95] text-[#48664d] font-black tracking-[-0.04em] sm:text-[56px]">
        <span className="text-[44px] sm:text-[56px]">草綠</span>
        <span className="pb-1 text-[20px] font-medium tracking-[-0.02em] text-[#48664d] sm:text-[24px]">
          ;초록
        </span>
      </h1>

      <p className="mt-2 text-[20px] leading-[1.6] font-semibold tracking-[-0.02em] text-ink-sub">
        기술 블로그(Technical Writing) 작성 에이전트
      </p>

      <div className="mt-12 space-y-4">
        <p className="mt-4 text-[16px] leading-[1.7] text-ink-sub">
          문체 그대로, 다음 글의 초안부터 퇴고까지
        </p>
        {ENTRIES.map(({ key, title, body, hint }) => (
          <button
            key={key}
            type="button"
            onClick={() => onStart(key)}
            className="w-full rounded-2xl border border-[#48664d]/30 bg-[#48664d]/10 px-6 py-7 text-left transition-all duration-200 hover:border-[#48664d] hover:bg-[#48664d]/15 active:scale-[0.99]"
          >
            <span className="block text-[19px] font-bold tracking-[-0.01em]">
              {title}
            </span>
            <span className="mt-3 block text-[13px] text-ink-sub">{hint}</span>
            <span className="mt-0 block text-[15px] leading-[1.5] text-ink-sub">
              {body}
            </span>
          </button>
        ))}
      </div>

      <p className="mt-16 border-t border-line pt-8 text-[13px] leading-[1.7] text-ink-sub">
        글을 통째로 모델에 밀어 넣지 않습니다. 
        문체를 규칙으로 압축해 넘기기때문에 참고할 글이 많아져도 비용이 그만큼 늘지 않습니다. 단계별로 쓴
        토큰은 결과 화면에서 확인할 수 있습니다.
      </p>
    </div>
  )
}
