"""파이프라인이 주고받는 자료구조.

핵심 설계 원칙: 소스(로컬 md / velog / 템플릿)가 무엇이든 StyleGuide 라는
동일한 형태로 수렴시킨 뒤 작가에게 넘긴다. 작가는 소스 종류를 알지 못한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["local", "upload", "velog", "template"]


@dataclass
class Post:
    """소스에서 읽어온 기존 글 한 편."""

    title: str
    body: str
    origin: str  # 파일 경로나 URL


@dataclass
class SourceSpec:
    """어디서 기존 글을 가져올지에 대한 명세."""

    type: SourceType
    path: str | None = None  # local: md 폴더 경로
    username: str | None = None  # velog: 사용자명
    template: str | None = None  # template: 템플릿 키
    # upload: 브라우저가 폴더에서 읽어 보낸 글. 서버가 사용자 파일시스템을
    # 뒤지지 않아도 되고, 서버와 브라우저가 다른 기계여도 동작한다.
    posts: list[Post] | None = None


@dataclass
class BriefSpec:
    """사용자가 입력하는 글 요청.

    독자와 분량은 받지 않는다. 독자는 문서 유형(doc_type)에 이미 담겨 있고,
    분량은 "소제목 최소 8개" 규칙과 유형 템플릿이 정한다.
    """

    topic: str
    doc_type: str  # doc_types.DOC_TYPES 의 키
    tone: str  # config.TONES 의 키. 글 다듬기에서는 빈 문자열.
    # 필자가 겪은 일·메모·코드 조각. 주제 한 줄만으로는 모델이 일반론으로
    # 본문을 채우므로, 글의 알맹이가 될 재료를 선택 입력으로 받는다.
    material: str = ""


# ── 분석가 산출물 ──────────────────────────────────────────────────────


class StyleGuide(BaseModel):
    """기존 글에서 추출한 문체 특징.

    원문을 그대로 싣지 않고 이 구조로 '압축'해서 작가에게 넘긴다.
    같은 정보를 원문으로 넘기면 토큰이 수십 배 들고, 작가 프롬프트에서
    주제 지시가 묻힌다.
    """

    tone: str = Field(description="전반적인 어투 (예: 담백한 존댓말, 구어체 반말)")
    sentence_ending: str = Field(description="문장 종결 어미 패턴")
    avg_paragraph_sentences: int = Field(description="문단당 평균 문장 수")
    heading_style: str = Field(description="소제목 작성 방식 (명사형/의문형/단계형 등)")
    code_example_ratio: str = Field(description="코드 예시 비중과 사용 방식")
    vocabulary: str = Field(description="자주 쓰는 어휘·표현, 외래어 표기 습관")
    structure_pattern: str = Field(description="글 전체의 전형적인 전개 구조")
    dos: list[str] = Field(description="이 필자를 흉내 내려면 반드시 지킬 것")
    donts: list[str] = Field(description="이 필자라면 하지 않을 것")
    referenced_posts: list[str] = Field(
        default_factory=list, description="요청 주제와 관련해 특히 참고한 글 제목"
    )

    def to_prompt_block(self) -> str:
        """작가 프롬프트에 끼워 넣을 텍스트로 직렬화."""
        return "\n".join(
            [
                f"- 어투: {self.tone}",
                f"- 문장 종결: {self.sentence_ending}",
                f"- 문단당 평균 문장 수: {self.avg_paragraph_sentences}",
                f"- 소제목 스타일: {self.heading_style}",
                f"- 코드 예시: {self.code_example_ratio}",
                f"- 어휘·표현: {self.vocabulary}",
                f"- 전개 구조: {self.structure_pattern}",
                "- 반드시 지킬 것:",
                *[f"    · {d}" for d in self.dos],
                "- 하지 말 것:",
                *[f"    · {d}" for d in self.donts],
            ]
        )


# ── 편집자 산출물 ──────────────────────────────────────────────────────


class EditNote(BaseModel):
    """모델이 낸 지적 하나. 재작성이 아니라 '지적'이라는 점이 중요하다."""

    kind: Literal["오타", "논리"] = Field(description="지적의 종류")
    location: str = Field(description="문제가 있는 위치 (소제목명 + 문단 번호)")
    problem: str = Field(description="무엇이 문제인지")
    suggestion: str = Field(description="대안 (해당 문장 범위로 한정)")


class EditReport(BaseModel):
    notes: list[EditNote] = Field(default_factory=list)
    overall: str = Field(default="", description="전체 총평 한두 문장")


class ReviewNote(BaseModel):
    """다듬기 결과의 지적 하나.

    source 가 핵심이다. 'auto' 는 코드가 확실히 판정한 것이고 'model' 은
    모델의 판단이다. 둘을 같은 무게로 나열하면 읽는 사람이 전부 의심하거나
    전부 믿게 되므로, 화면에서 구분해 보여준다.
    """

    kind: Literal["오타", "논리", "형식"]
    source: Literal["auto", "model"]
    location: str
    problem: str
    suggestion: str


@dataclass
class ReviewResult:
    notes: list[ReviewNote]
    overall: str
    usage: list["StageUsage"] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usage)

    @property
    def auto_count(self) -> int:
        return sum(1 for n in self.notes if n.source == "auto")


# ── 파이프라인 결과 ────────────────────────────────────────────────────


@dataclass
class StageUsage:
    """단계별 토큰 사용량. 화면·발표자료에 그대로 올라간다."""

    stage: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    requests: int
    seconds: float = 0.0  # 이 단계(kickoff) 의 벽시계 소요 시간


@dataclass
class PipelineResult:
    style_guide: StyleGuide
    draft_markdown: str
    usage: list[StageUsage] = field(default_factory=list)
    sample_titles: list[str] = field(default_factory=list)
    sample_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usage)
