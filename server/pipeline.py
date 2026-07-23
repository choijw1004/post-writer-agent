"""파이프라인 진입점.

CLI 도 FastAPI 도 이 함수 하나만 부른다. 인터페이스(입출력 방식)와 파이프라인을
분리해 두면 나중에 React 화면을 붙일 때 로직을 건드릴 일이 없다.

단계를 Crew 하나에 몰아넣지 않고 단계마다 Crew 를 따로 kickoff 하는 이유는
두 가지다.
- 단계별 토큰 사용량을 정확히 분리해 계측할 수 있다(채점 대응 항목).
- 진행 상황을 단계 경계에서 콜백으로 흘려보낼 수 있다(뒤에 SSE 를 붙일 자리).
"""

from __future__ import annotations

from typing import Callable

from crewai import Crew, Process

from server import tasks, tokens
from server.agents import analyst_agent, editor_agent, writer_agent
from server.models import (
    BriefSpec,
    EditReport,
    PipelineResult,
    SourceSpec,
    StyleGuide,
)
from server.sources import load_posts

# (stage, status, data) — data 는 그 단계가 만들어낸 중간 산출물이다.
# 화면은 파이프라인이 다 끝나기를 기다리지 않고 단계별로 결과를 보여준다.
ProgressFn = Callable[[str, str, dict | None], None]


def _noop(stage: str, status: str, data: dict | None = None) -> None:
    pass


def _run_stage(agent, task, stage: str, usages: list) -> object:
    """에이전트 하나 + Task 하나짜리 Crew 를 돌리고 토큰 사용량을 적립한다."""
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )
    output = crew.kickoff()
    usages.append(tokens.usage_from_crew_output(stage, output.token_usage))
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
    audience: str,
    purpose: str,
    length: str,
    on_progress: ProgressFn = _noop,
) -> PipelineResult:
    """기존 글 → 문체 분석 → 초안 생성 → 편집 검토까지 한 번에 실행한다."""
    brief = BriefSpec(topic=topic, audience=audience, purpose=purpose, length=length)
    usages: list = []

    # ── 0. 소스 로드 + 토큰 예산으로 샘플 선별 ────────────────────────
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

    # ── 1. 분석가 ────────────────────────────────────────────────────
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
    on_progress("write", "done", {"draft_markdown": draft})

    # ── 3. 편집자 ────────────────────────────────────────────────────
    on_progress("edit", "start")
    editor = editor_agent()
    editing_out = _run_stage(
        editor,
        tasks.editing_task(editor, draft, brief),
        "편집자",
        usages,
    )
    edit_report = editing_out.pydantic
    if not isinstance(edit_report, EditReport):
        edit_report = EditReport(notes=[], overall=editing_out.raw.strip())
    on_progress("edit", "done", {"edit_report": edit_report.model_dump()})

    return PipelineResult(
        style_guide=style_guide,
        draft_markdown=draft,
        edit_report=edit_report,
        usage=usages,
        sample_titles=[p.title for p in samples],
        sample_tokens=sample_tokens,
    )
