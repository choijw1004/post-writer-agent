"""생성 작업(job) 관리.

파이프라인 한 번이 수십 초 걸린다. HTTP 요청 하나로 붙잡고 있으면 프론트가
진행 상황을 보여줄 방법이 없고, 프록시 타임아웃에도 걸린다. 그래서 작업을
job 으로 만들어 백그라운드 스레드에서 돌리고, 진행 상황은 따로 구독하게 한다.

CrewAI 호출은 동기 코드라 asyncio 로 감싸도 이벤트 루프를 막는다.
그래서 별도 스레드에서 실행한다.
"""

from __future__ import annotations

import threading
import traceback
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field

from server.models import PipelineResult, ReviewResult, SourceSpec
from server.pipeline import run_pipeline, run_review

# 메모리에만 두는 저장소다. 서버를 재시작하면 사라진다. 수업 데모 범위에서는
# 충분하고, 필요해지면 이 클래스만 갈아 끼우면 된다.
MAX_JOBS = 32


@dataclass
class Job:
    id: str
    kind: str = "draft"  # draft(초안 작성) | review(글 다듬기)
    status: str = "running"  # running | done | error
    events: list[dict] = field(default_factory=list)
    result: PipelineResult | ReviewResult | None = None
    error: str | None = None

    def emit(
        self,
        stage: str,
        status: str,
        message: str = "",
        data: dict | None = None,
    ) -> None:
        self.events.append(
            {"stage": stage, "status": status, "message": message, "data": data}
        )


class JobStore:
    def __init__(self, max_jobs: int = MAX_JOBS) -> None:
        self._jobs: OrderedDict[str, Job] = OrderedDict()
        self._lock = threading.Lock()
        self._max_jobs = max_jobs

    def create(self, kind: str = "draft") -> Job:
        job = Job(id=uuid.uuid4().hex[:12], kind=kind)
        with self._lock:
            self._jobs[job.id] = job
            while len(self._jobs) > self._max_jobs:
                self._jobs.popitem(last=False)  # 오래된 것부터 버린다
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)


store = JobStore()


def _spawn(job: Job, work) -> Job:
    """work() 를 백그라운드 스레드에서 돌리고 결과·실패를 job 에 옮긴다.

    초안 작성과 다듬기가 이 함수를 공유한다. 실패 처리와 완료 이벤트가 두
    군데로 갈라지지 않게 하려는 것이다.
    """

    def run() -> None:
        try:
            result = work()
        except Exception as exc:  # noqa: BLE001 - 어떤 실패든 job 상태로 옮긴다
            job.error = f"{type(exc).__name__}: {exc}"
            job.status = "error"
            job.emit("error", "error", job.error)
            traceback.print_exc()
            return

        job.result = result
        job.status = "done"
        job.emit("complete", "done", f"총 {result.total_tokens:,} 토큰")

    threading.Thread(target=run, name=f"job-{job.id}", daemon=True).start()
    return job


def start_job(
    source: SourceSpec,
    topic: str,
    doc_type: str,
    tone: str,
    material: str = "",
) -> Job:
    """초안 작성 job."""
    job = store.create(kind="draft")
    job.emit("queued", "start", "생성 준비 중")

    return _spawn(
        job,
        lambda: run_pipeline(
            source=source,
            topic=topic,
            doc_type=doc_type,
            tone=tone,
            material=material,
            on_progress=lambda stage, status, data=None: job.emit(
                stage, status, data=data
            ),
        ),
    )


def start_review(draft: str, doc_type: str) -> Job:
    """글 다듬기 job. 편집자 1회 호출이라 초안 작성보다 훨씬 빨리 끝난다."""
    job = store.create(kind="review")
    job.emit("queued", "start", "검토 준비 중")

    return _spawn(
        job,
        lambda: run_review(
            draft=draft,
            doc_type=doc_type,
            on_progress=lambda stage, status, data=None: job.emit(
                stage, status, data=data
            ),
        ),
    )
