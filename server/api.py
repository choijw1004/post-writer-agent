"""FastAPI 앱.

    .venv/bin/uvicorn server.api:app --reload --port 8000

CLI 와 완전히 같은 run_pipeline() 을 부른다. 이 파일에는 HTTP 처리만 있고
생성 로직은 한 줄도 없다.

진행 상황 전달은 SSE(/stream)를 기본으로 하고, 폴링(/jobs/{id})도 함께 연다.
SSE 가 프록시나 브라우저 확장에 막히는 경우가 있어 데모 당일 대비용이다.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from server import config, jobs
from server.doc_types import DOC_TYPES
from server.models import SourceSpec
from server.sources import parse_markdown
from server.schemas import (
    GenerateRequest,
    JobCreated,
    JobStatusOut,
    OptionsResponse,
    ResultOut,
    ReviewJobStatusOut,
    ReviewRequest,
    ReviewResultOut,
)

app = FastAPI(
    title="blog-agent",
    description="기존 글의 문체를 학습해 새 블로그 초안을 생성한다.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE 폴링 간격. 화면의 단계 표시가 이보다 빠를 필요는 없다.
_POLL_INTERVAL = 0.25


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": config.MODEL}


@app.get("/api/options", response_model=OptionsResponse)
def options() -> OptionsResponse:
    """프론트의 선택지 목록. 서버가 단일 출처다."""
    return OptionsResponse(
        doc_types=list(DOC_TYPES),
        doc_type_spec={name: d.when for name, d in DOC_TYPES.items()},
        tones=config.TONES,
        tone_spec=config.TONE_SPEC,
        model=config.MODEL,
    )


@app.post("/api/jobs", response_model=JobCreated, status_code=202)
def create_job(req: GenerateRequest) -> JobCreated:
    """생성 작업을 만들고 즉시 job_id 를 돌려준다(비동기)."""
    # 업로드된 마크다운은 여기서 Post 로 바꾼다. 파싱 규칙(제목 찾는 순서 등)은
    # 로컬 폴더를 직접 읽을 때와 같은 함수를 쓴다.
    posts = None
    if req.source_type == "upload":
        parsed = [parse_markdown(f.name, f.content) for f in req.files]
        posts = [p for p in parsed if p is not None]
        if not posts:
            raise HTTPException(
                status_code=422,
                detail="선택한 폴더의 마크다운이 모두 비어 있습니다.",
            )

    source = SourceSpec(
        type=req.source_type,
        path=req.path,
        username=req.username,
        template=req.template,
        posts=posts,
    )
    job = jobs.start_job(
        source=source,
        topic=req.topic,
        doc_type=req.doc_type,
        tone=req.tone,
        material=req.material,
    )
    return JobCreated(job_id=job.id, status=job.status)


@app.post("/api/reviews", response_model=JobCreated, status_code=202)
def create_review(req: ReviewRequest) -> JobCreated:
    """글 다듬기 작업을 만든다. 소스도 주제도 필요 없고 글만 받는다."""
    job = jobs.start_review(draft=req.draft, doc_type=req.doc_type)
    return JobCreated(job_id=job.id, status=job.status)


@app.get("/api/reviews/{job_id}", response_model=ReviewJobStatusOut)
def get_review(job_id: str) -> ReviewJobStatusOut:
    job = jobs.store.get(job_id)
    if job is None or job.kind != "review":
        raise HTTPException(status_code=404, detail="job 을 찾을 수 없습니다.")

    return ReviewJobStatusOut(
        job_id=job.id,
        status=job.status,
        events=job.events,
        result=ReviewResultOut.from_review(job.result) if job.result else None,
        error=job.error,
    )


@app.get("/api/jobs/{job_id}", response_model=JobStatusOut)
def get_job(job_id: str) -> JobStatusOut:
    """폴링용. 지금까지의 이벤트와, 끝났다면 결과까지 함께 준다."""
    job = jobs.store.get(job_id)
    if job is None or job.kind != "draft":
        raise HTTPException(status_code=404, detail="job 을 찾을 수 없습니다.")

    return JobStatusOut(
        job_id=job.id,
        status=job.status,
        events=job.events,
        result=ResultOut.from_pipeline(job.result) if job.result else None,
        error=job.error,
    )


def _stream(job_id: str, kind: str, serialize) -> StreamingResponse:
    """SSE. 새 이벤트가 생길 때마다 흘려보내고, 끝나면 result 를 한 번 보낸다.

    초안 작성과 다듬기가 이 함수를 공유한다. 다른 것은 결과를 어떤 스키마로
    직렬화하느냐뿐이다.
    """
    job = jobs.store.get(job_id)
    if job is None or job.kind != kind:
        raise HTTPException(status_code=404, detail="job 을 찾을 수 없습니다.")

    async def event_source():
        sent = 0
        while True:
            # 파이프라인은 다른 스레드에서 events 에 append 만 한다.
            # 읽는 쪽은 인덱스만 앞으로 밀면 되므로 락이 필요 없다.
            while sent < len(job.events):
                event = job.events[sent]
                sent += 1
                yield f"event: progress\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

            if job.status in {"done", "error"} and sent >= len(job.events):
                break

            await asyncio.sleep(_POLL_INTERVAL)

        if job.status == "done" and job.result is not None:
            payload = serialize(job.result).model_dump_json()
            yield f"event: result\ndata: {payload}\n\n"
        else:
            payload = json.dumps({"error": job.error}, ensure_ascii=False)
            yield f"event: failed\ndata: {payload}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # nginx 뒤에서 버퍼링되지 않게
        },
    )


@app.get("/api/jobs/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    return _stream(job_id, "draft", ResultOut.from_pipeline)


@app.get("/api/reviews/{job_id}/stream")
async def stream_review(job_id: str) -> StreamingResponse:
    return _stream(job_id, "review", ReviewResultOut.from_review)
