import { useState } from 'react'

import { createJob } from './api'
import BackButton from './components/BackButton'
import ChoiceList from './components/ChoiceList'
import ErrorNote from './components/ErrorNote'
import FolderPicker from './components/FolderPicker'
import GeneratingView from './components/GeneratingView'
import PrimaryButton from './components/PrimaryButton'
import ResultView from './components/ResultView'
import StepShell from './components/StepShell'
import TextField from './components/TextField'
import { useJobRun } from './useJobRun'

// 한 화면에 한 가지만 묻는다. 그래서 폼 하나가 아니라 단계 목록이다.
// 독자·분량은 묻지 않는다. 독자는 문서 유형에 담겨 있고 분량은 규칙이 정한다.
const STEPS = ['source', 'topic', 'doc_type', 'tone']
const TOTAL = STEPS.length

// 편집자는 '글 다듬기'로 옮겼다. 초안 작성은 분석과 작성 두 단계다.
const STAGES = [
  { key: 'analyze', label: '문체 분석' },
  { key: 'write', label: '초안 작성' },
]

const SOURCE_OPTIONS = [
  { value: 'upload', label: '내 컴퓨터의 마크다운 폴더' },
  { value: 'velog', label: 'velog' },
  { value: 'template', label: '아직 쓴 글이 없어요' },
]

const SOURCE_HINT = {
  upload: 'GitHub Pages 블로그의 _posts 같은 폴더',
  velog: '사용자명으로 최근 글을 불러옵니다',
  template: '문체 분석 없이 기본 문체로 시작합니다',
}

const EMPTY_FORM = {
  source_type: 'upload',
  username: '',
  topic: '',
  doc_type: '',
  tone: '',
}

export default function DraftFlow({ options, model, onHome, onReview }) {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(EMPTY_FORM)
  const [folder, setFolder] = useState(null)

  const job = useJobRun('/api/jobs')

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))
  const next = () => setStep((s) => Math.min(s + 1, TOTAL - 1))
  const back = () => (step === 0 ? onHome() : setStep((s) => s - 1))

  const pick = (key) => (value) => {
    set(key, value)
    next()
  }

  function restart() {
    job.reset()
    setForm(EMPTY_FORM)
    setFolder(null)
    setStep(0)
  }

  function start(tone) {
    set('tone', tone)
    const body = { ...form, tone }
    if (form.source_type === 'upload' && folder) {
      body.files = folder.files
      body.folder_name = folder.folderName
    }
    job.run(() => createJob(body))
  }

  if (job.phase === 'done' && job.result) {
    return (
      <ResultView
        result={job.result}
        model={model}
        onRestart={restart}
        onReview={onReview}
      />
    )
  }

  if (job.phase === 'running') {
    return (
      <GeneratingView
        stages={STAGES}
        done={job.done}
        current={job.current}
        styleGuide={job.stageData.style_guide}
        sampleTitles={job.stageData.sample_titles}
      />
    )
  }

  const stepName = STEPS[step]
  const sourceReady =
    form.source_type === 'upload'
      ? Boolean(folder)
      : form.source_type === 'velog'
        ? Boolean(form.username.trim())
        : true // template: 필요한 입력이 없다

  return (
    <>
      <BackButton onClick={back} />

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

          {form.source_type === 'upload' && (
            <div className="mt-8 space-y-6">
              <FolderPicker value={folder} onPick={setFolder} />
              <PrimaryButton onClick={next} disabled={!sourceReady}>
                다음
              </PrimaryButton>
            </div>
          )}

          {form.source_type === 'velog' && (
            <div className="mt-8 space-y-6">
              <TextField
                value={form.username}
                onChange={(v) => set('username', v)}
                onEnter={() => sourceReady && next()}
                placeholder="velopert"
                aria-label="velog 사용자명"
                prefix="@"
              />
              <PrimaryButton onClick={next} disabled={!sourceReady}>
                다음
              </PrimaryButton>
            </div>
          )}

          {form.source_type === 'template' && (
            <div className="mt-8 space-y-6">
              <p className="rounded-2xl bg-surface px-5 py-4 text-[14px] leading-[1.6] text-ink-sub">
                담백한 기술 블로그 기본 문체로 씁니다. 문체 분석 단계를
                건너뛰기 때문에 그만큼 빠르고, 토큰도 들지 않아요. 나중에 쓴
                글이 쌓이면 그 글로 내 문체를 만들 수 있습니다.
              </p>
              <PrimaryButton onClick={next}>다음</PrimaryButton>
            </div>
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

      {stepName === 'doc_type' && options && (
        <StepShell
          step={3}
          total={TOTAL}
          title="어떤 유형의 글인가요?"
          description="유형이 글의 구조를 정합니다. 독자가 언제 찾아 읽는 글인지로 골라주세요."
        >
          <ChoiceList
            options={options.doc_types}
            value={form.doc_type}
            hint={options.doc_type_spec}
            onSelect={pick('doc_type')}
          />
        </StepShell>
      )}

      {stepName === 'tone' && options && (
        <StepShell step={4} total={TOTAL} title="어떤 말투로 쓸까요?">
          <ChoiceList
            options={options.tones}
            value={form.tone}
            hint={options.tone_spec}
            onSelect={start}
          />
        </StepShell>
      )}

      <ErrorNote message={job.error} />
    </>
  )
}
