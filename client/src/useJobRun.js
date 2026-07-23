import { useEffect, useRef, useState } from 'react'

import { subscribeJob } from './api'

/**
 * job 하나의 생애를 들고 있는 훅.
 *
 * 초안 작성과 다듬기가 이걸 공유한다. 둘 다 "만들고 → 진행 이벤트를 받고 →
 * 결과를 받는다"는 모양이 같고, 다른 것은 만드는 방법과 구독할 경로뿐이다.
 */
export function useJobRun(base) {
  const [phase, setPhase] = useState('idle') // idle | running | done | error
  const [done, setDone] = useState([])
  const [current, setCurrent] = useState(null)
  const [stageData, setStageData] = useState({}) // 단계별 중간 산출물
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const unsubscribe = useRef(null)

  useEffect(() => () => unsubscribe.current?.(), [])

  function reset() {
    unsubscribe.current?.()
    unsubscribe.current = null
    setPhase('idle')
    setDone([])
    setCurrent(null)
    setStageData({})
    setResult(null)
    setError(null)
  }

  /** @param create job 을 만들고 {job_id} 를 돌려주는 함수 */
  async function run(create) {
    reset()
    setPhase('running')

    try {
      const { job_id: jobId } = await create()

      unsubscribe.current = subscribeJob(jobId, {
        base,
        onProgress: ({ stage, status, data }) => {
          if (status === 'start') setCurrent(stage)
          if (status === 'done') {
            setDone((prev) => (prev.includes(stage) ? prev : [...prev, stage]))
          }
          if (data) setStageData((prev) => ({ ...prev, ...data }))
        },
        onResult: (payload) => {
          setResult(payload)
          setPhase('done')
        },
        onError: (message) => {
          setError(message)
          setPhase('error')
        },
      })
    } catch (err) {
      setError(String(err))
      setPhase('error')
    }
  }

  return { phase, done, current, stageData, result, error, run, reset }
}
