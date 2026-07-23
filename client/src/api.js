// FastAPI 와 이야기하는 유일한 곳. 컴포넌트는 fetch 를 직접 부르지 않는다.
// 개발 중에는 vite 프록시가 /api 를 8000 포트로 넘긴다.

async function json(res) {
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status} ${detail}`)
  }
  return res.json()
}

export function fetchOptions() {
  return fetch('/api/options').then(json)
}

function post(path, body) {
  return fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(json)
}

// 초안 작성
export function createJob(body) {
  return post('/api/jobs', body)
}

// 글 다듬기
export function createReview(body) {
  return post('/api/reviews', body)
}

/**
 * job 의 진행 상황을 구독한다.
 *
 * SSE 를 먼저 쓰고, 연결이 열리지 않으면 폴링으로 내려간다. 서버가 두 경로를
 * 모두 열어둔 이유가 이것이다(발표 당일 SSE 가 막히는 경우 대비).
 *
 * 초안 작성(/api/jobs)과 다듬기(/api/reviews)가 같은 구조라 base 만 다르다.
 *
 * @returns {() => void} 구독 해제 함수
 */
export function subscribeJob(jobId, { onProgress, onResult, onError, base = '/api/jobs' }) {
  const source = new EventSource(`${base}/${jobId}/stream`)
  let settled = false
  let pollTimer = null

  const close = () => {
    source.close()
    if (pollTimer) clearInterval(pollTimer)
  }

  source.addEventListener('progress', (e) => {
    onProgress(JSON.parse(e.data))
  })

  source.addEventListener('result', (e) => {
    settled = true
    onResult(JSON.parse(e.data))
    close()
  })

  source.addEventListener('failed', (e) => {
    settled = true
    onError(JSON.parse(e.data).error ?? '알 수 없는 오류')
    close()
  })

  source.onerror = () => {
    if (settled) return // 정상 종료 후의 error 이벤트는 무시한다
    source.close()
    startPolling()
  }

  function startPolling() {
    if (pollTimer) return
    let sent = 0
    pollTimer = setInterval(async () => {
      try {
        const res = await fetch(`${base}/${jobId}`)
        const job = await res.json()
        job.events.slice(sent).forEach((event) => {
          sent += 1
          onProgress(event)
        })
        if (job.status === 'done') {
          settled = true
          onResult(job.result)
          close()
        } else if (job.status === 'error') {
          settled = true
          onError(job.error)
          close()
        }
      } catch (err) {
        settled = true
        onError(String(err))
        close()
      }
    }, 700)
  }

  return close
}
