import { useEffect, useRef, useState } from 'react'

import { createJob, fetchOptions, subscribeJob } from './api'
import ChoiceList from './components/ChoiceList'
import GeneratingView from './components/GeneratingView'
import PrimaryButton from './components/PrimaryButton'
import ResultView from './components/ResultView'
import StepShell from './components/StepShell'
import TextField from './components/TextField'

// 한 화면에 한 가지만 묻는다. 그래서 폼 하나가 아니라 단계 목록이다.
const STEPS = ['source', 'topic', 'audience', 'purpose', 'length']
const TOTAL = STEPS.length

const SOURCE_OPTIONS = [
  { value: 'local', label: '내 컴퓨터의 마크다운 폴더' },
  { value: 'velog', label: 'velog' },
  { value: 'template', label: '아직 쓴 글이 없어요' },
]

const SOURCE_HINT = {
  local: 'GitHub Pages 블로그의 _posts 같은 폴더',
  velog: '준비 중',
  template: '준비 중',
}

const EMPTY_FORM = {
  source_type: 'local',
  path: './sample_posts',
  topic: '',
  audience: '',
  purpose: '',
  length: '',
}

export default function App() {
  const [options, setOptions] = useState(null)
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(EMPTY_FORM)

  const [phase, setPhase] = useState('form') // form | generating | result
  const [done, setDone] = useState([])
  const [current, setCurrent] = useState(null)
  const [styleGuide, setStyleGuide] = useState(null)
  const [sampleTitles, setSampleTitles] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const unsubscribe = useRef(null)

  useEffect(() => {
    fetchOptions()
      .then(setOptions)
      .catch(() =>
        setError('서버에 연결하지 못했습니다. FastAPI 가 떠 있는지 확인하세요.'),
      )

    return () => unsubscribe.current?.()
  }, [])

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))
  const next = () => setStep((s) => Math.min(s + 1, TOTAL - 1))
  const back = () => setStep((s) => Math.max(s - 1, 0))

  const pick = (key) => (value) => {
    set(key, value)
    next()
  }

  const reset = () => {
    unsubscribe.current?.()
    setForm(EMPTY_FORM)
    setStep(0)
    setPhase('form')
    setDone([])
    setCurrent(null)
    setStyleGuide(null)
    setSampleTitles([])
    setResult(null)
    setError(null)
  }

  async function start(length) {
    const body = { ...form, length }
    set('length', length)
    setPhase('generating')
    setError(null)

    try {
      const { job_id: jobId } = await createJob(body)

      unsubscribe.current = subscribeJob(jobId, {
        onProgress: (event) => {
          const { stage, status, data } = event

          if (status === 'start') setCurrent(stage)
          if (status === 'done') {
            setDone((prev) => (prev.includes(stage) ? prev : [...prev, stage]))
          }

          // 각 단계가 내놓은 중간 산출물을 그때그때 화면에 반영한다.
          if (data?.style_guide) setStyleGuide(data.style_guide)
          if (data?.sample_titles) setSampleTitles(data.sample_titles)
        },
        onResult: (payload) => {
          setResult(payload)
          setPhase('result')
        },
        onError: (message) => {
          setError(message)
          setPhase('form')
        },
      })
    } catch (err) {
      setError(String(err))
      setPhase('form')
    }
  }

  if (phase === 'result' && result) {
    return <ResultView result={result} model={options?.model} onRestart={reset} />
  }

  if (phase === 'generating') {
    return (
      <GeneratingView
        done={done}
        current={current}
        styleGuide={styleGuide}
        sampleTitles={sampleTitles}
      />
    )
  }

  const stepName = STEPS[step]

  return (
    <>
      {step > 0 && (
        <button
          type="button"
          onClick={back}
          className="fixed top-6 left-6 rounded-xl px-3 py-2 text-[15px] text-ink-sub transition-colors duration-200 hover:text-ink"
        >
          ← 이전
        </button>
      )}

      {stepName === 'source' && (
        <StepShell
          step={1}
          total={TOTAL}
          title="어떤 글의 문체를 따라갈까요?"
          description="기존 글에서 문체를 뽑아내 새 글에 입힙니다."
        >
          <ChoiceList
            options={SOURCE_OPTIONS}
            value={form.source_type}
            hint={SOURCE_HINT}
            onSelect={(value) => set('source_type', value)}
          />

          {form.source_type === 'local' ? (
            <div className="mt-8 space-y-6">
              <TextField
                value={form.path}
                onChange={(v) => set('path', v)}
                onEnter={next}
                placeholder="./sample_posts"
                aria-label="마크다운 폴더 경로"
              />
              <PrimaryButton onClick={next} disabled={!form.path.trim()}>
                다음
              </PrimaryButton>
            </div>
          ) : (
            <p className="mt-8 rounded-2xl bg-surface px-5 py-4 text-[14px] leading-[1.6] text-ink-sub">
              아직 연결되지 않은 경로입니다. 지금은 마크다운 폴더로만 생성할 수
              있어요.
            </p>
          )}
        </StepShell>
      )}

      {stepName === 'topic' && (
        <StepShell step={2} total={TOTAL} title="어떤 글을 쓸까요?">
          <div className="space-y-6">
            <TextField
              value={form.topic}
              onChange={(v) => set('topic', v)}
              onEnter={() => form.topic.trim() && next()}
              placeholder="예) 파이썬 타입 힌트를 실무에 도입한 이야기"
              aria-label="글 주제"
              autoFocus
            />
            <PrimaryButton onClick={next} disabled={!form.topic.trim()}>
              다음
            </PrimaryButton>
          </div>
        </StepShell>
      )}

      {stepName === 'audience' && options && (
        <StepShell step={3} total={TOTAL} title="누가 읽을 글인가요?">
          <ChoiceList
            options={options.audiences}
            value={form.audience}
            onSelect={pick('audience')}
          />
        </StepShell>
      )}

      {stepName === 'purpose' && options && (
        <StepShell step={4} total={TOTAL} title="왜 쓰는 글인가요?">
          <ChoiceList
            options={options.purposes}
            value={form.purpose}
            onSelect={pick('purpose')}
          />
        </StepShell>
      )}

      {stepName === 'length' && options && (
        <StepShell step={5} total={TOTAL} title="얼마나 길게 쓸까요?">
          <ChoiceList
            options={options.lengths}
            value={form.length}
            hint={options.length_spec}
            onSelect={start}
          />
        </StepShell>
      )}

      {error && (
        <div className="mx-auto max-w-[560px] px-6 pb-16">
          <p className="rounded-2xl bg-red-50 px-5 py-4 text-[14px] leading-[1.6] text-red-600">
            {error}
          </p>
        </div>
      )}
    </>
  )
}
