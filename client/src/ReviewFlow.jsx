import { useState } from 'react'

import { createReview } from './api'
import BackButton from './components/BackButton'
import ChoiceList from './components/ChoiceList'
import DraftInput from './components/DraftInput'
import ErrorNote from './components/ErrorNote'
import GeneratingView from './components/GeneratingView'
import PrimaryButton from './components/PrimaryButton'
import ReviewResultView from './components/ReviewResultView'
import StepShell from './components/StepShell'
import { useJobRun } from './useJobRun'

const STEPS = ['draft', 'audience', 'purpose']
const TOTAL = STEPS.length

// 형식 검사는 토큰을 쓰지 않아 순식간에 끝난다. 그래도 점을 하나 두는 이유는,
// 자동 검사가 별도의 층이라는 걸 진행 중에도 보이게 하려는 것이다.
const STAGES = [
  { key: 'check', label: '형식 검사' },
  { key: 'edit', label: '오타·논리' },
]

export default function ReviewFlow({ options, model, seed = '', onHome }) {
  const [step, setStep] = useState(seed ? 1 : 0) // 초안에서 넘어왔으면 글은 이미 있다
  const [draft, setDraft] = useState(seed)
  const [audience, setAudience] = useState('')

  const job = useJobRun('/api/reviews')

  const next = () => setStep((s) => Math.min(s + 1, TOTAL - 1))
  const back = () => (step === 0 ? onHome() : setStep((s) => s - 1))

  function restart() {
    job.reset()
    setDraft('')
    setAudience('')
    setStep(0)
  }

  function start(purpose) {
    job.run(() => createReview({ draft, audience, purpose }))
  }

  if (job.phase === 'done' && job.result) {
    return (
      <ReviewResultView result={job.result} model={model} onRestart={restart} />
    )
  }

  if (job.phase === 'running') {
    return <GeneratingView stages={STAGES} done={job.done} current={job.current} />
  }

  const stepName = STEPS[step]

  return (
    <>
      <BackButton onClick={back} />

      {stepName === 'draft' && (
        <StepShell
          step={1}
          total={TOTAL}
          title="어떤 글을 다듬을까요?"
          description="글을 고쳐주지는 않습니다. 어디가 왜 문제인지만 짚어드립니다."
        >
          <div className="space-y-6">
            <DraftInput value={draft} onChange={setDraft} />
            <PrimaryButton onClick={next} disabled={!draft.trim()}>
              다음
            </PrimaryButton>
          </div>
        </StepShell>
      )}

      {stepName === 'audience' && options && (
        <StepShell
          step={2}
          total={TOTAL}
          title="누가 읽을 글인가요?"
          description="독자에 따라 어디까지 설명이 필요한지가 달라집니다."
        >
          <ChoiceList
            options={options.audiences}
            value={audience}
            onSelect={(value) => {
              setAudience(value)
              next()
            }}
          />
        </StepShell>
      )}

      {stepName === 'purpose' && options && (
        <StepShell step={3} total={TOTAL} title="왜 쓴 글인가요?">
          <ChoiceList options={options.purposes} value="" onSelect={start} />
        </StepShell>
      )}

      <ErrorNote message={job.error} />
    </>
  )
}
