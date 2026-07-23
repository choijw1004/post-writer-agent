import PrimaryButton from './PrimaryButton'

// 이름 이야기를 한 줄로만 한다. 랜딩에서 설명이 길어지면 시작 버튼이 밀린다.
const STEPS = [
  {
    n: '01',
    title: '문체를 읽어냅니다',
    body: '이미 써둔 글에서 어투·문단 길이·소제목 방식·코드 비중을 규칙으로 옮겨 적습니다.',
  },
  {
    n: '02',
    title: '그 문체로 씁니다',
    body: '주제와 독자만 정하면 됩니다. 작가는 문체 규칙만 보고 쓰기 때문에 글이 남의 것처럼 되지 않습니다.',
  },
  {
    n: '03',
    title: '고치지 않고 짚어줍니다',
    body: '검토자는 원고를 대신 고쳐 쓰지 않습니다. 어디가 왜 문제인지만 알려주고, 반영은 직접 정합니다.',
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
        초록(抄錄)은 요점을 뽑아 적는다는 뜻입니다. 이미 써둔 글에서 문체를 뽑아
        적어두고, 그 문체로 새 글의 초안을 씁니다.
      </p>

      <div className="mt-10">
        <PrimaryButton onClick={onStart}>시작하기</PrimaryButton>
      </div>

      <p className="mt-4 text-center text-[13px] text-ink-sub">
        마크다운 폴더나 velog 계정이면 됩니다
      </p>

      <div className="mt-20 space-y-10 border-t border-line pt-14">
        {STEPS.map(({ n, title, body }) => (
          <div key={n}>
            <p className="text-[13px] font-semibold text-brand">{n}</p>
            <h2 className="mt-2 text-[17px] font-bold tracking-[-0.01em]">{title}</h2>
            <p className="mt-2 text-[15px] leading-[1.65] text-ink-sub">{body}</p>
          </div>
        ))}
      </div>

      <p className="mt-20 border-t border-line pt-8 text-[13px] leading-[1.7] text-ink-sub">
        글을 통째로 모델에 밀어 넣지 않습니다. 문체를 규칙으로 압축해 넘기기
        때문에 참고할 글이 많아져도 비용이 그만큼 늘지 않습니다. 단계별로 쓴
        토큰은 결과 화면에서 확인할 수 있습니다.
      </p>
    </div>
  )
}
