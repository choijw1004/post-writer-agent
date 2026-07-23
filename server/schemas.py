"""HTTP 경계에서만 쓰는 요청·응답 스키마.

파이프라인 내부 자료구조(server/models.py)와 분리해 둔다. 내부 구조를 바꿔도
API 계약이 따라 흔들리지 않게 하려는 것이고, 반대로 API 에 필드를 더해도
파이프라인은 모르게 하려는 것이다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from server import config
from server.models import PipelineResult, ReviewResult


class UploadedFile(BaseModel):
    """브라우저가 폴더에서 읽어 보낸 마크다운 하나."""

    name: str
    content: str


class GenerateRequest(BaseModel):
    source_type: Literal["local", "upload", "velog", "template"] = "upload"
    path: str | None = Field(default=None, description="local 소스: 마크다운 폴더 경로")
    files: list[UploadedFile] = Field(
        default_factory=list, description="upload 소스: 폴더에서 읽은 마크다운"
    )
    folder_name: str | None = Field(default=None, description="upload 소스: 폴더 이름")
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
        if self.source_type == "velog" and not self.username:
            raise ValueError("velog 소스는 username 이 필요합니다.")
        if self.source_type == "upload":
            if not self.files:
                raise ValueError("선택한 폴더에서 마크다운 파일을 찾지 못했습니다.")
            if len(self.files) > config.UPLOAD_MAX_FILES:
                raise ValueError(
                    f"마크다운이 너무 많습니다 (최대 {config.UPLOAD_MAX_FILES}개). "
                    "글이 더 적은 폴더를 골라 주세요."
                )
            total = sum(len(f.content) for f in self.files)
            if total > config.UPLOAD_MAX_CHARS:
                raise ValueError(
                    f"글이 너무 큽니다 ({total:,}자, 최대 "
                    f"{config.UPLOAD_MAX_CHARS:,}자)."
                )
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


class ResultOut(BaseModel):
    style_guide: StyleGuideOut
    draft_markdown: str
    usage: UsageOut

    @classmethod
    def from_pipeline(cls, result: PipelineResult) -> "ResultOut":
        return cls(
            style_guide=StyleGuideOut(**result.style_guide.model_dump()),
            draft_markdown=result.draft_markdown,
            usage=UsageOut(
                stages=[StageUsageOut(**vars(u)) for u in result.usage],
                total_prompt_tokens=sum(u.prompt_tokens for u in result.usage),
                total_completion_tokens=sum(u.completion_tokens for u in result.usage),
                total_tokens=result.total_tokens,
                sample_titles=result.sample_titles,
                sample_tokens=result.sample_tokens,
            ),
        )


class ReviewRequest(BaseModel):
    """글 다듬기 요청. 소스도 주제도 필요 없고 글 자체만 받는다."""

    draft: str = Field(min_length=1)
    audience: str
    purpose: str

    @model_validator(mode="after")
    def check_choices(self) -> "ReviewRequest":
        if self.audience not in config.AUDIENCES:
            raise ValueError(f"audience 는 {config.AUDIENCES} 중 하나여야 합니다.")
        if self.purpose not in config.PURPOSES:
            raise ValueError(f"purpose 는 {config.PURPOSES} 중 하나여야 합니다.")
        if len(self.draft) > config.REVIEW_MAX_CHARS:
            raise ValueError(
                f"글이 너무 깁니다 ({len(self.draft):,}자, 최대 "
                f"{config.REVIEW_MAX_CHARS:,}자)."
            )
        return self


class ReviewNoteOut(BaseModel):
    kind: str
    source: str  # auto(코드가 확정) | model(모델의 판단)
    location: str
    problem: str
    suggestion: str


class ReviewResultOut(BaseModel):
    notes: list[ReviewNoteOut]
    overall: str
    auto_count: int
    model_count: int
    usage: list[StageUsageOut]
    total_tokens: int

    @classmethod
    def from_review(cls, result: ReviewResult) -> "ReviewResultOut":
        notes = [ReviewNoteOut(**n.model_dump()) for n in result.notes]
        return cls(
            notes=notes,
            overall=result.overall,
            auto_count=result.auto_count,
            model_count=len(notes) - result.auto_count,
            usage=[StageUsageOut(**vars(u)) for u in result.usage],
            total_tokens=result.total_tokens,
        )


class ReviewJobStatusOut(BaseModel):
    job_id: str
    status: Literal["running", "done", "error"]
    events: list["ProgressEvent"]
    result: ReviewResultOut | None = None
    error: str | None = None


class ProgressEvent(BaseModel):
    stage: str
    status: str
    message: str = ""
    # 그 단계가 만들어낸 중간 산출물. 화면은 이걸로 분석 결과를 먼저 그린다.
    data: dict | None = None


class JobCreated(BaseModel):
    job_id: str
    status: str


class JobStatusOut(BaseModel):
    job_id: str
    status: Literal["running", "done", "error"]
    events: list[ProgressEvent]
    result: ResultOut | None = None
    error: str | None = None
