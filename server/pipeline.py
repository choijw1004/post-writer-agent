"""파이프라인 진입점. 두 개다.

- run_pipeline()  초안 작성: 기존 글 → 문체 분석 → 초안. 결과는 복사해 가는 글.
- run_review()    글 다듬기: 이미 있는 글 → 결정적 검사 + 편집자 → 지적 목록.

둘을 한 파이프라인의 앞뒤 단계로 묶지 않은 이유가 있다. 그렇게 묶으면 이미
글을 써둔 사람은 검토에 도달할 방법이 없다. 초안 생성을 먼저 거쳐야 하기
때문이다. 사용자가 도구를 찾는 시점이 서로 다르므로 진입점을 나눈다.

CLI 도 FastAPI 도 이 두 함수만 부른다. 인터페이스(입출력 방식)와 파이프라인을
분리해 두면 화면을 바꿔도 로직을 건드릴 일이 없다.

단계를 Crew 하나에 몰아넣지 않고 단계마다 Crew 를 따로 kickoff 하는 이유는
두 가지다.
- 단계별 토큰 사용량을 정확히 분리해 계측할 수 있다(채점 대응 항목).
- 진행 상황을 단계 경계에서 콜백으로 흘려보낼 수 있다(SSE 를 붙인 자리).
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from crewai import Crew, Process

from server import checks, config, style_presets, tasks, tokens
from server.agents import analyst_agent, editor_agent, writer_agent
from server.models import (
    BriefSpec,
    EditReport,
    PipelineResult,
    ReviewNote,
    ReviewResult,
    SourceSpec,
    StyleGuide,
)
from server.sources import load_posts

# (stage, status, data) — data 는 그 단계가 만들어낸 중간 산출물이다.
# 화면은 파이프라인이 다 끝나기를 기다리지 않고 단계별로 결과를 보여준다.
ProgressFn = Callable[[str, str, dict | None], None]

# kickoff 실행 로그를 남기는 로거. 핸들러는 붙이지 않는다(라이브러리 관례).
# 출력 여부·형식은 진입점(CLI 등)이 정하고, 서버 SSE 경로는 건드리지 않는다.
log = logging.getLogger("cholog.pipeline")


def _noop(stage: str, status: str, data: dict | None = None) -> None:
    pass


def _run_stage(agent, task, stage: str, usages: list) -> object:
    """에이전트 하나 + Task 하나짜리 Crew 를 돌리고 토큰 사용량을 적립한다.

    kickoff 경계마다 실행 로그(호출 수·토큰·소요 시간)를 남긴다. 단계마다
    Crew 를 따로 돌리기 때문에, 이 로그가 곧 파이프라인의 실행 기록이 된다.
    """
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )
    log.info("kickoff ▶ %s", stage)
    started = time.perf_counter()
    output = crew.kickoff()
    elapsed = time.perf_counter() - started

    usage = tokens.usage_from_crew_output(stage, output.token_usage, seconds=elapsed)
    usages.append(usage)
    log.info(
        "kickoff ✓ %s · %d호출 · in=%d out=%d 합계=%d · %.2fs",
        stage,
        usage.requests,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.total_tokens,
        elapsed,
    )
    return output


def _strip_code_fence(text: str) -> str:
    """모델이 전체를 ```markdown 으로 감쌌을 때만 벗겨낸다."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if len(lines) < 2 or not lines[-1].strip().startswith("```"):
        return stripped
    return "\n".join(lines[1:-1]).strip()


def run_pipeline(
    source: SourceSpec,
    topic: str,
    doc_type: str,
    tone: str,
    material: str = "",
    on_progress: ProgressFn = _noop,
) -> PipelineResult:
    """기존 글 → 문체 분석 → 초안 생성까지 실행한다."""
    brief = BriefSpec(topic=topic, doc_type=doc_type, tone=tone, material=material)
    usages: list = []

    if source.type == "template":
        # 쓴 글이 없는 사용자. 분석할 원문이 없으므로 로드·분석을 건너뛰고
        # 기본 문체를 쓴다. 토큰 0.
        style_guide = style_presets.DEFAULT_STYLE_GUIDE
        samples: list = []
        sample_tokens = 0
        on_progress(
            "analyze",
            "done",
            {"style_guide": style_guide.model_dump(), "preset": True},
        )
    else:
        # ── 0. 소스 로드 + 토큰 예산으로 샘플 선별 ────────────────────
        on_progress("load", "start")
        posts = load_posts(source)
        samples, sample_tokens = tokens.select_style_samples(posts)
        on_progress(
            "load",
            "done",
            {
                "found": len(posts),
                "selected": len(samples),
                "sample_titles": [p.title for p in samples],
                "sample_tokens": sample_tokens,
            },
        )

        # ── 1. 분석가 ────────────────────────────────────────────────
        on_progress("analyze", "start")
        analyst = analyst_agent()
        analysis_out = _run_stage(
            analyst,
            tasks.analysis_task(analyst, samples, brief),
            "분석가",
            usages,
        )
        style_guide = analysis_out.pydantic
        if not isinstance(style_guide, StyleGuide):
            raise RuntimeError("분석가가 StyleGuide 형식을 반환하지 않았습니다.")
        # 문체 분석 결과는 작가가 글을 다 쓸 때까지 기다리지 않고 바로 내보낸다.
        on_progress("analyze", "done", {"style_guide": style_guide.model_dump()})

    # ── 2. 작가 ──────────────────────────────────────────────────────
    # 작가에게 넘어가는 것은 style_guide 와 brief 뿐이다. 원문도, 소스 종류도
    # 넘기지 않는다.
    on_progress("write", "start")
    writer = writer_agent()
    writing_out = _run_stage(
        writer,
        tasks.writing_task(writer, style_guide, brief),
        "작가",
        usages,
    )
    draft = _strip_code_fence(writing_out.raw)

    # 소제목 최소 개수는 코드로 센다. 모자라면 보강 Task 를 한 번만 더 돌린다.
    # 처음부터 다시 쓰게 하지 않는 이유는 편집자와 같다 — 자기회귀 생성은
    # 전문 재생성 시 잘 쓴 절까지 함께 바꿔버린다.
    heading_count = checks.count_subheadings(draft)
    if heading_count < config.MIN_SUBHEADINGS:
        expand_out = _run_stage(
            writer,
            tasks.expand_task(writer, draft, brief, current=heading_count),
            "작가(보강)",
            usages,
        )
        expanded = _strip_code_fence(expand_out.raw)
        # 보강본이 조건을 더 잘 지킬 때만 채택한다. 나빠졌으면 원본 유지.
        if checks.count_subheadings(expanded) > heading_count:
            draft = expanded

    on_progress("write", "done", {"draft_markdown": draft})

    # 초안 작성은 여기서 끝난다. 검토는 '글 다듬기'(run_review)의 몫이다.
    return PipelineResult(
        style_guide=style_guide,
        draft_markdown=draft,
        usage=usages,
        sample_titles=[p.title for p in samples],
        sample_tokens=sample_tokens,
    )


def run_review(
    draft: str,
    doc_type: str,
    on_progress: ProgressFn = _noop,
) -> ReviewResult:
    """이미 있는 글에서 오타와 논리 문제를 찾는다. 글을 고쳐주지는 않는다.

    두 층으로 나뉜다.
    - 결정적 검사: 코드로 확실히 판정되는 것. 토큰 0, 즉시.
    - 편집자: 오타와 논리. 모델의 판단이라 확실하지 않다.

    두 층을 섞지 않고 note 마다 source 를 남기는 게 이 기능의 핵심이다.
    확실한 지적과 추측을 같은 무게로 나열하면 읽는 사람이 전부 의심하거나
    전부 믿게 된다.
    """
    usages: list = []

    # ── 1. 결정적 검사 (LLM 없음) ────────────────────────────────────
    on_progress("check", "start")
    auto_notes = checks.run_checks(draft)
    on_progress("check", "done", {"auto_count": len(auto_notes)})

    # ── 2. 편집자 ────────────────────────────────────────────────────
    on_progress("edit", "start")
    brief = BriefSpec(topic="", doc_type=doc_type, tone="")
    editor = editor_agent()
    editing_out = _run_stage(
        editor,
        # 자동 검사가 이미 찾은 것을 함께 넘겨 중복 지적을 막는다.
        tasks.editing_task(editor, draft, brief, already_found=auto_notes),
        "편집자",
        usages,
    )

    report = editing_out.pydantic
    if not isinstance(report, EditReport):
        report = EditReport(notes=[], overall=editing_out.raw.strip())

    model_notes = [
        ReviewNote(
            kind=note.kind,
            source="model",
            location=note.location,
            problem=note.problem,
            suggestion=note.suggestion,
        )
        for note in report.notes
    ]
    # 프롬프트로 막아도 모델이 자동 검사와 같은 지적을 반복한다. 코드로 거른다.
    model_notes = checks.drop_overlapping(auto_notes, model_notes)
    on_progress("edit", "done")

    # 확실한 것부터 보여준다.
    return ReviewResult(
        notes=auto_notes + model_notes,
        overall=report.overall,
        usage=usages,
    )
