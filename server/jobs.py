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

from server.models import PipelineResult, SourceSpec
from server.pipeline import run_pipeline

# 메모리에만 두는 저장소다. 서버를 재시작하면 사라진다. 수업 데모 범위에서는
# 충분하고, 필요해지면 이 클래스만 갈아 끼우면 된다.
MAX_JOBS = 32


@dataclass
class Job:
    id: str
    status: str = "running"  # running | done | error
    events: list[dict] = field(default_factory=list)
    result: PipelineResult | None = None
    error: str | None = None

    def emit(self, stage: str, status: str, message: str = "") -> None:
        self.events.append({"stage": stage, "status": status, "message": message})


class JobStore:
    def __init__(self, max_jobs: int = MAX_JOBS) -> None:
        self._jobs: OrderedDict[str, Job] = OrderedDict()
        self._lock = threading.Lock()
        self._max_jobs = max_jobs

    def create(self) -> Job:
        job = Job(id=uuid.uuid4().hex[:12])
        with self._lock:
            self._jobs[job.id] = job
            while len(self._jobs) > self._max_jobs:
                self._jobs.popitem(last=False)  # 오래된 것부터 버린다
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)


store = JobStore()


def start_job(
    source: SourceSpec,
    topic: str,
    audience: str,
    purpose: str,
    length: str,
) -> Job:
    """job 을 만들고 백그라운드 스레드에서 파이프라인을 돌린다."""
    job = store.create()
    job.emit("queued", "start", "생성 준비 중")

    def run() -> None:
        try:
            result = run_pipeline(
                source=source,
                topic=topic,
                audience=audience,
                purpose=purpose,
                length=length,
                on_progress=lambda stage, status: job.emit(
                    stage,
                    status if status in {"start", "done"} else "info",
                    "" if status in {"start", "done"} else status,
                ),
            )
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
