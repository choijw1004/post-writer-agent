import ProgressDots from './ProgressDots'
import StyleGuideCard from './StyleGuideCard'

const MESSAGE = {
  load: '기존 글을 읽고 있어요',
  analyze: '문체를 분석하고 있어요',
  write: '초안을 쓰고 있어요',
  edit: '읽어보며 검토하고 있어요',
}

export default function GeneratingView({ done, current, styleGuide, sampleTitles }) {
  return (
    <div className="step-in mx-auto w-full max-w-[560px] px-6 pt-24 pb-24">
      <h1 className="text-center text-[22px] font-bold tracking-[-0.02em]">
        {MESSAGE[current] ?? '거의 다 됐어요'}
      </h1>

      <div className="mt-12">
        <ProgressDots done={done} current={current} />
      </div>

      {/* 분석이 끝나는 즉시 결과를 띄운다. 초안을 기다리는 동안 빈 화면을
          보지 않아도 되고, 어떤 문체를 잡았는지 먼저 확인할 수 있다. */}
      {styleGuide && (
        <div className="mt-14">
          <StyleGuideCard styleGuide={styleGuide} sampleTitles={sampleTitles} />
        </div>
      )}
    </div>
  )
}
