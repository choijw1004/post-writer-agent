// 진행 표시는 점 3개가 순서대로 채워지는 정도로만.
// 에이전트 이름·로그·소요 시간을 늘어놓지 않는다. 기술 정보는 결과 화면
// 하단의 접히는 영역으로 보낸다.
const STAGES = [
  { key: 'analyze', label: '문체 분석' },
  { key: 'write', label: '초안 작성' },
  { key: 'edit', label: '검토' },
]

export default function ProgressDots({ done, current }) {
  return (
    <div className="flex items-center justify-center gap-8">
      {STAGES.map(({ key, label }) => {
        const isDone = done.includes(key)
        const isCurrent = current === key

        return (
          <div key={key} className="flex flex-col items-center gap-3">
            <span
              className={`h-2.5 w-2.5 rounded-full transition-all duration-200 ${
                isDone
                  ? 'bg-brand'
                  : isCurrent
                    ? 'animate-pulse bg-brand'
                    : 'bg-line'
              }`}
            />
            <span
              className={`text-[13px] transition-colors duration-200 ${
                isDone || isCurrent ? 'font-medium text-ink' : 'text-ink-sub'
              }`}
            >
              {label}
            </span>
          </div>
        )
      })}
    </div>
  )
}
