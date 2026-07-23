import ReviewNotes from './ReviewNotes'

// 다듬기 결과. 토큰 표는 초안 작성과 같은 자리(하단 접힘)에 둔다.
export default function ReviewResultView({ result, model, onRestart }) {
  return (
    <div className="step-in mx-auto w-full max-w-[720px] px-6 pt-16 pb-24">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-[26px] font-bold tracking-[-0.02em]">다 읽었습니다</h1>
        <button
          type="button"
          onClick={onRestart}
          className="rounded-xl px-4 py-2 text-[14px] font-medium text-ink-sub transition-colors duration-200 hover:text-ink"
        >
          다른 글 보기
        </button>
      </div>

      <div className="mt-10">
        <ReviewNotes result={result} />
      </div>

      <details className="mt-10 rounded-2xl border border-line bg-surface">
        <summary className="flex cursor-pointer list-none items-center justify-between px-6 py-4 text-[14px] text-ink-sub transition-colors duration-200 hover:text-ink">
          <span>
            토큰 사용량 · 누적{' '}
            <span className="font-semibold text-ink">
              {result.total_tokens.toLocaleString()}
            </span>
          </span>
          <span>⌄</span>
        </summary>
        <div className="border-t border-line px-6 py-5 text-[13px] leading-[1.7] text-ink-sub">
          <p>
            자동 검사 {result.auto_count}건은 코드로 판정해서 토큰을 쓰지 않았고,
            모델 판단 {result.model_count}건에만 {result.total_tokens.toLocaleString()}{' '}
            토큰이 들었습니다. 확실히 판정되는 것을 모델에게 물으면 답이 흔들리기만
            하고 비용이 더 듭니다.
          </p>
          <p className="mt-2">모델: {model}</p>
        </div>
      </details>
    </div>
  )
}
