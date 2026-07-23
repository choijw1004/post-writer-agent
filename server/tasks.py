"""Task 정의.

각 description 에 ReAct(Thought → Action → Observation) 절차를 실제로 적는다.
"단계별로 생각하라"는 말만 얹는 것과 달리, 무엇을 관찰하고 무엇을 결정할지를
명시하면 모델이 중간 근거를 실제로 생성하고, 그 토큰들이 뒤이은 결론 토큰의
어텐션 대상이 된다.
"""

from __future__ import annotations

from crewai import Agent, Task

from server import config
from server.doc_types import DOC_TYPES
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
    doc = DOC_TYPES[brief.doc_type]
    tone_spec = config.TONE_SPEC.get(brief.tone, brief.tone)
    minimum = config.MIN_SUBHEADINGS
    return Task(
        description=(
            f"""아래 문서 유형 템플릿과 문체 가이드를 지켜서 블로그 글 초안을 쓰세요.

[글 요청]
- 주제: {brief.topic}
- 문서 유형: {brief.doc_type} — {doc.when} 읽는 글
- 말투: {brief.tone} — {tone_spec}

[문서 유형 템플릿]
{doc.template}

[문체 가이드]
{style_guide.to_prompt_block()}

[우선순위 — 지시가 서로 어긋날 때]
1. 글의 구조는 문서 유형 템플릿을 따른다. 문체 가이드의 '전개 구조'보다 우선한다.
2. 말투는 위 [글 요청]의 말투({brief.tone})를 따른다. 문체 가이드의 '어투',
   '문장 종결'보다 우선한다.
3. 그 밖의 것(어휘, 문단 길이, 코드 비중, 소제목 표현 방식)은 문체 가이드를 따른다.

다음 ReAct 절차를 밟으세요.

Thought: 주제 "{brief.topic}" 를 "{brief.doc_type}" 로 쓴다면, 템플릿의 각
  섹션에 무엇이 들어가야 하는가? 이 유형을 찾아 읽는 사람은 {doc.when}
  찾아온 사람이므로, 그 사람이 원하는 것부터 채운다.

Action: 템플릿을 바탕으로 소제목 뼈대를 먼저 잡는다. 대괄호 자리는 주제에
  맞는 실제 제목으로 바꾼다. 템플릿의 골격은 최소 기준이다 — 반복 가능한
  섹션(단계, 해결 방법 등)을 내용에 맞게 늘리고, 주제를 제대로 다루는 데
  필요한 절(배경, 흔한 실수, 한계와 대안, 실전 팁 등)을 더한다.

Observation: 뼈대의 소제목(## 과 ###) 개수를 센다. {minimum}개 미만이면 단계를
  더 쪼개거나 절을 더해 {minimum}개 이상으로 만든다. 이때 개수를 채우려고
  알맹이 없는 절을 만들지 않는다. 쓸 내용이 있는 절만 세운다.

최종 결론: 뼈대를 채워 본문을 쓴다. 글자 수 제한은 없다. 각 섹션을 제대로
  설명하는 데 필요한 만큼 쓴다.

[반드시 지킬 것]
- 출력은 마크다운 본문만. 설명이나 머리말을 앞에 붙이지 않는다.
- 최상단에 `# 제목` 을 한 줄 넣는다.
- 소제목(`##` 또는 `###`)을 최소 {minimum}개 이상 둔다.
- 각 소제목 아래에 실질 내용을 둔다. 산문이면 두 문단 이상, 코드 중심이면
  코드 블록과 그 설명 한 문단 이상. 한두 문장짜리 절을 만들지 않는다.
- 코드와 명령은 실제로 실행 가능한 형태로 쓰고, 바로 뒤에 실행 결과나
  확인 방법을 붙인다.
- 템플릿의 대괄호 안내문(`[...]`)을 출력에 그대로 남기지 않는다.
- 말투({brief.tone})를 처음부터 끝까지 유지한다.
- 코드 예시는 문체 가이드가 말하는 비중에 맞추되, 문서 유형이 코드를
  요구하면(참조 문서의 시그니처 등) 넣는다.
- 사실을 지어내지 않는다. 확실하지 않은 수치나 버전은 쓰지 않고 넘어간다.
- 문체 가이드의 donts 를 어기지 않는다."""
        ),
        expected_output=(
            f"마크다운 블로그 초안 전문. 소제목 {minimum}개 이상. 코드펜스로 "
            "전체를 감싸지 말고 마크다운 본문 자체를 출력할 것."
        ),
        agent=agent,
    )


def expand_task(agent: Agent, draft: str, brief: BriefSpec, current: int) -> Task:
    """소제목이 모자랄 때 한 번만 부르는 보강 Task.

    모델은 프롬프트 지시만으로는 개수를 자주 틀린다. 다시 처음부터 쓰게 하면
    이미 잘 쓴 절까지 함께 바뀌므로, 기존 본문은 그대로 두고 절만 더하게 한다.
    """
    minimum = config.MIN_SUBHEADINGS
    tone_spec = config.TONE_SPEC.get(brief.tone, brief.tone)
    return Task(
        description=(
            f"""아래 초안의 소제목(##, ###)은 {current}개입니다. 절을 더해 소제목을
최소 {minimum}개로 늘리세요.

[반드시 지킬 것]
- 이미 있는 제목·소제목·문단은 지우거나 고쳐 쓰지 않는다. 그대로 옮긴다.
- 주제 "{brief.topic}" 를 실제로 풍성하게 하는 절만 더한다. 배경, 작동 원리,
  흔한 실수, 한계와 대안, 실전 팁 등에서 고른다.
- 새 절에도 실질 내용을 넣는다. 산문이면 두 문단 이상, 코드 중심이면 코드
  블록과 설명 한 문단 이상.
- 새 절의 말투는 기존 본문과 같게 유지한다: {brief.tone} — {tone_spec}
- 출력은 완성된 마크다운 전문만. 무엇을 더했는지 설명하지 않는다.

--- 초안 ---
{draft}
--- 초안 끝 ---"""
        ),
        expected_output=(
            f"기존 내용이 보존되고 소제목이 {minimum}개 이상으로 늘어난 "
            "마크다운 전문."
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

    doc = DOC_TYPES[brief.doc_type]
    return Task(
        description=(
            f"""아래 글을 검토하세요. 이 글은 "{brief.doc_type}" 유형입니다.
{doc.when} 찾아 읽는 글입니다.

당신이 볼 것은 두 가지뿐입니다.

1. 오타 — 맞춤법, 띄어쓰기, 조사 오류, 잘못 쓴 단어
2. 논리 — 근거 없이 결론으로 건너뛴 곳, 앞뒤 문단이 서로 어긋나는 곳,
   설명 없이 튀어나온 용어, 문단 연결이 끊기는 지점

다음 ReAct 절차를 밟으세요.

Thought: {doc.when} 이 글을 찾아온 사람이라면 어디서 막힐 것인가?

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
