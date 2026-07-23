import { useEffect, useState } from 'react'

import { fetchOptions } from './api'
import ErrorNote from './components/ErrorNote'
import Landing from './components/Landing'
import DraftFlow from './DraftFlow'
import ReviewFlow from './ReviewFlow'

// 진입점이 둘이고, 둘은 서로 독립적이다. 여기서는 어느 쪽에 있는지와
// 서버에서 받은 선택지만 들고 있는다.
export default function App() {
  const [options, setOptions] = useState(null)
  const [optionsError, setOptionsError] = useState(null)
  const [mode, setMode] = useState('landing') // landing | draft | review
  const [seedDraft, setSeedDraft] = useState('')

  useEffect(() => {
    fetchOptions()
      .then(setOptions)
      .catch(() =>
        setOptionsError(
          '서버에 연결하지 못했습니다. FastAPI 가 떠 있는지 확인하세요.',
        ),
      )
  }, [])

  const goHome = () => {
    setSeedDraft('')
    setMode('landing')
  }

  if (mode === 'draft') {
    return (
      <DraftFlow
        options={options}
        model={options?.model}
        onHome={goHome}
        // 초안을 복사해 다시 붙여넣게 하지 않고 그대로 넘긴다.
        onReview={(draft) => {
          setSeedDraft(draft)
          setMode('review')
        }}
      />
    )
  }

  if (mode === 'review') {
    return (
      <ReviewFlow
        options={options}
        model={options?.model}
        seed={seedDraft}
        onHome={goHome}
      />
    )
  }

  return (
    <>
      <Landing onStart={setMode} />
      <ErrorNote message={optionsError} />
    </>
  )
}
