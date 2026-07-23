"""Task 정의.

각 description 에 ReAct(Thought → Action → Observation) 절차를 실제로 적는다.
"단계별로 생각하라"는 말만 얹는 것과 달리, 무엇을 관찰하고 무엇을 결정할지를
명시하면 모델이 중간 근거를 실제로 생성하고, 그 토큰들이 뒤이은 결론 토큰의
어텐션 대상이 된다.
"""

from __future__ import annotations

from crewai import Agent, Task

from server import config
from server.models import BriefSpec, EditReport, Post, StyleGuide


def format_samples(posts: list[Post]) -> str:
    blocks = []
    for i, post in enumerate(posts, start=1):
        blocks.append(f"### 샘플 {i}: {post.title}\n{post.body}")
    return "\n\n".join(blocks)


def analysis_task(agent: Agent, posts: list[Post], brief: BriefSpec) -> Task:
    return Task(
        description=(
            f"""아래는 한 필자가 쓴 기존 블로그 글 {len(posts)}편의 발췌입니다.
이 필자의 문체를 다른 사람이 재현할 수 있도록 규칙으로 옮겨 적으세요.

이번에 새로 쓸 글의 주제는 "{brief.topic}" 입니다.

다음 ReAct 절차를 순서대로 밟으세요.

Thought: 문체를 재현하려면 무엇을 측정해야 하는가?
  - 어투와 문장 종결 어미
  - 문단 길이(문단당 몇 문장인지)
  - 소제목을 명사형으로 다는지, 질문형인지, 단계형인지
  - 코드 블록이 글에서 차지하는 비중과 등장 방식
  - 반복적으로 쓰는 어휘·접속 표현·외래어 표기 습관
  - 글 전체의 전개 순서

Action: 위 항목을 샘플에서 하나씩 확인한다. 인상이 아니라 실제 문장을 근거로
  삼는다. 동시에 주제 "{brief.topic}" 과 내용이 가까운 샘플을 골라 둔다.

Observation: 확인한 내용을 적는다. 이때 '친근하다', '읽기 쉽다' 같은 평가어는
  쓰지 않는다. 대신 '~합니다체를 기본으로 쓰고 문단 끝에서만 ~죠 로 끝낸다'
  처럼, 읽는 사람이 그대로 따라 할 수 있는 형태로 적는다.

최종 결론: 관찰 결과를 정해진 스키마로 정리한다.
  - dos 와 donts 는 각각 3개 이상, 실행 가능한 지시문으로 적는다.
  - referenced_posts 에는 주제와 가까워 특히 참고한 샘플의 제목을 넣는다.

--- 기존 글 발췌 ---
{format_samples(posts)}
--- 발췌 끝 ---"""
        ),
        expected_output=(
            "StyleGuide 스키마를 채운 결과. 모든 필드를 한국어로 채우고, "
            "dos/donts 는 각각 3개 이상."
        ),
        agent=agent,
        output_pydantic=StyleGuide,
    )


def writing_task(agent: Agent, style_guide: StyleGuide, brief: BriefSpec) -> Task:
    length_spec = config.LENGTH_SPEC.get(brief.length, brief.length)
    return Task(
        description=(
            f"""아래 문체 가이드를 지켜서 블로그 글 초안을 쓰세요.

[글 요청]
- 주제: {brief.topic}
- 독자: {brief.audience}
- 목적: {brief.purpose}
- 분량: {brief.length} ({length_spec})

[문체 가이드]
{style_guide.to_prompt_block()}

다음 ReAct 절차를 밟으세요.

Thought: 이 주제를 이 독자에게, 이 목적으로 전달하려면 어떤 순서가 맞는가?
  독자가 "{brief.audience}" 이므로 어디까지가 이미 아는 내용이고 어디부터
  설명이 필요한지 먼저 정한다. 목적이 "{brief.purpose}" 이므로 글의 무게중심을
  어디에 둘지 정한다.

Action: 소제목만으로 뼈대를 먼저 잡는다. 뼈대가 문체 가이드의 '전개 구조',
  '소제목 스타일' 과 어긋나지 않는지 대조한다.

Observation: 뼈대가 분량 조건({length_spec})에 맞는지 센다. 소제목 수가
  모자라거나 넘치면 뼈대를 고친다.

최종 결론: 뼈대를 채워 본문을 쓴다.

[반드시 지킬 것]
- 출력은 마크다운 본문만. 설명이나 머리말을 앞에 붙이지 않는다.
- 최상단에 `# 제목` 을 한 줄 넣는다.
- 코드 예시는 문체 가이드가 말하는 비중에 맞춘다. 가이드가 코드를 거의 쓰지
  않는다고 했다면 억지로 넣지 않는다.
- 사실을 지어내지 않는다. 확실하지 않은 수치나 버전은 쓰지 않고 넘어간다.
- 문체 가이드의 donts 를 어기지 않는다."""
        ),
        expected_output=(
            "마크다운 블로그 초안 전문. 코드펜스로 전체를 감싸지 말고 "
            "마크다운 본문 자체를 출력할 것."
        ),
        agent=agent,
    )


def editing_task(
    agent: Agent,
    draft: str,
    brief: BriefSpec,
    already_found: list | None = None,
) -> Task:
    """오타와 논리만 본다.

    코드 문법·제목 단계·링크처럼 기계적으로 판정되는 것은 server/checks.py 가
    이미 잡아두었으므로 여기서 다시 묻지 않는다. 확실히 판정할 수 있는 것을
    모델에게 물으면 답이 흔들리기만 하고 토큰만 더 든다.

    already_found 로 자동 검사 결과를 함께 넘긴다. "코드 문법은 보지 마라"는
    금지만으로는 모델이 눈앞의 깨진 코드를 그냥 지나치지 못한다. 무엇이 이미
    처리됐는지 구체적으로 알려주는 편이 확실하다.

    바깥 사실(존재하는 API 인지, 수치가 맞는지)은 검사 범위가 아니다.
    """
    if already_found:
        found_block = "\n".join(
            f"  · {note.location}: {note.problem}" for note in already_found
        )
        already_block = (
            "\n[별도 검사에서 이미 찾은 것 — 다시 적지 마세요]\n" + found_block + "\n"
        )
    else:
        already_block = ""

    return Task(
        description=(
            f"""아래 글을 검토하세요. 대상 독자는 "{brief.audience}", 글의 목적은
"{brief.purpose}" 입니다.

당신이 볼 것은 두 가지뿐입니다.

1. 오타 — 맞춤법, 띄어쓰기, 조사 오류, 잘못 쓴 단어
2. 논리 — 근거 없이 결론으로 건너뛴 곳, 앞뒤 문단이 서로 어긋나는 곳,
   대상 독자에게 설명 없이 튀어나온 용어, 문단 연결이 끊기는 지점

다음 ReAct 절차를 밟으세요.

Thought: 이 글의 독자가 "{brief.audience}" 라면 어디서 막힐 것인가?

Action: 글을 위에서부터 훑으며 위 두 종류에 해당하는 지점을 찾는다.
  각 지점이 어느 소제목 아래 몇 번째 문단인지 기록한다.

Observation: 찾은 것들을 중요한 순서로 정렬한다. 사소한 취향 차이는 버린다.

최종 결론: 지적 목록을 만든다. 각 항목의 kind 는 '오타' 또는 '논리' 입니다.

[절대 지킬 규칙]
- 글 전문을 다시 쓰지 마세요. 수정된 원고를 출력하는 것은 금지입니다.
- 대안(suggestion)은 문제가 된 문장 범위로만 한정합니다. 문단 전체나 절 전체를
  새로 쓴 버전을 제시하지 마세요.
- 다음은 검사 범위가 아닙니다. 적지 마세요.
    · 코드의 문법 오류, 코드블록 언어 표기, 제목 단계, 링크 주소
      (별도 검사에서 이미 처리했습니다)
    · 사실 확인이 필요한 것 (수치가 맞는지, 그 API 가 실제로 있는지)
    · 문체나 어투에 대한 취향
- 지적은 최대 8개까지. 억지로 채우지 말고 실제로 문제인 것만 적으세요.
- 문제가 거의 없다면 notes 를 짧게 두고 overall 에 그렇게 적으세요.
{already_block}
--- 검토할 글 ---
{draft}
--- 글 끝 ---"""
        ),
        expected_output=(
            "EditReport 스키마. notes 의 각 항목은 kind(오타|논리)/위치/문제/대안이 "
            "채워져 있고, 수정된 원고 전문은 어디에도 포함되지 않아야 한다."
        ),
        agent=agent,
        output_pydantic=EditReport,
    )
