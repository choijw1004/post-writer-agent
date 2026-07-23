"""HTTP 경계에서만 쓰는 요청·응답 스키마.

파이프라인 내부 자료구조(server/models.py)와 분리해 둔다. 내부 구조를 바꿔도
API 계약이 따라 흔들리지 않게 하려는 것이고, 반대로 API 에 필드를 더해도
파이프라인은 모르게 하려는 것이다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from server import config
from server.models import PipelineResult


class GenerateRequest(BaseModel):
    source_type: Literal["local", "velog", "template"] = "local"
    path: str | None = Field(default=None, description="local 소스: 마크다운 폴더 경로")
    username: str | None = Field(default=None, description="velog 소스: 사용자명")
    template: str | None = Field(default=None, description="template 소스: 템플릿 키")

    topic: str = Field(min_length=1, max_length=200)
    audience: str
    purpose: str
    length: str

    @model_validator(mode="after")
    def check_choices(self) -> "GenerateRequest":
        if self.audience not in config.AUDIENCES:
            raise ValueError(f"audience 는 {config.AUDIENCES} 중 하나여야 합니다.")
        if self.purpose not in config.PURPOSES:
            raise ValueError(f"purpose 는 {config.PURPOSES} 중 하나여야 합니다.")
        if self.length not in config.LENGTHS:
            raise ValueError(f"length 는 {config.LENGTHS} 중 하나여야 합니다.")
        if self.source_type == "local" and not self.path:
            raise ValueError("local 소스는 path 가 필요합니다.")
        return self


class OptionsResponse(BaseModel):
    """프론트가 선택지를 하드코딩하지 않도록 서버가 내려준다."""

    audiences: list[str]
    purposes: list[str]
    lengths: list[str]
    length_spec: dict[str, str]
    model: str


class StageUsageOut(BaseModel):
    stage: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    requests: int


class UsageOut(BaseModel):
    stages: list[StageUsageOut]
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    sample_titles: list[str]
    sample_tokens: int


class StyleGuideOut(BaseModel):
    tone: str
    sentence_ending: str
    avg_paragraph_sentences: int
    heading_style: str
    code_example_ratio: str
    vocabulary: str
    structure_pattern: str
    dos: list[str]
    donts: list[str]
    referenced_posts: list[str]


class EditNoteOut(BaseModel):
    location: str
    problem: str
    suggestion: str


class EditReportOut(BaseModel):
    notes: list[EditNoteOut]
    overall: str


class ResultOut(BaseModel):
    style_guide: StyleGuideOut
    draft_markdown: str
    edit_report: EditReportOut
    usage: UsageOut

    @classmethod
    def from_pipeline(cls, result: PipelineResult) -> "ResultOut":
        return cls(
            style_guide=StyleGuideOut(**result.style_guide.model_dump()),
            draft_markdown=result.draft_markdown,
            edit_report=EditReportOut(**result.edit_report.model_dump()),
            usage=UsageOut(
                stages=[StageUsageOut(**vars(u)) for u in result.usage],
                total_prompt_tokens=sum(u.prompt_tokens for u in result.usage),
                total_completion_tokens=sum(u.completion_tokens for u in result.usage),
                total_tokens=result.total_tokens,
                sample_titles=result.sample_titles,
                sample_tokens=result.sample_tokens,
            ),
        )


class ProgressEvent(BaseModel):
    stage: str
    status: str
    message: str = ""


class JobCreated(BaseModel):
    job_id: str
    status: str


class JobStatusOut(BaseModel):
    job_id: str
    status: Literal["running", "done", "error"]
    events: list[ProgressEvent]
    result: ResultOut | None = None
    error: str | None = None
