// 모든 단계가 공유하는 껍데기.
// 여백을 여기 한 곳에서만 정한다. 화면마다 제각각 잡으면 리듬이 깨진다.
export default function StepShell({ step, total, title, description, children }) {
  return (
    <div className="step-in mx-auto w-full max-w-[560px] px-6 pt-20 pb-24">
      {step != null && (
        <p className="mb-3 text-[13px] font-medium tracking-wide text-ink-sub">
          {step} / {total}
        </p>
      )}

      <h1 className="text-[26px] leading-[1.35] font-bold tracking-[-0.02em]">
        {title}
      </h1>

      {description && (
        <p className="mt-3 text-[15px] leading-[1.6] text-ink-sub">{description}</p>
      )}

      {/* 제목과 본문 사이를 넉넉히 띄운다. 이게 인상의 8할이다. */}
      <div className="mt-10">{children}</div>
    </div>
  )
}
