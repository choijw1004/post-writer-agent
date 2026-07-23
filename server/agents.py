"""에이전트 3종.

한 프롬프트에 분석·작성·검토를 다 넣지 않고 셋으로 쪼갠 이유:
(1) Self-Attention 은 시퀀스 길이에 대해 N^2 로 비용이 늘어난다. 긴 프롬프트
    하나보다 짧은 프롬프트 셋이 싸다.
(2) 길어질수록 지시가 서로 희석된다. 역할을 나누면 각 호출에서 모델이
    주목해야 할 지시가 적어진다.
"""

from __future__ import annotations

from crewai import LLM, Agent

from server import config


def build_llm(temperature: float) -> LLM:
    return LLM(model=config.MODEL, temperature=temperature)


def analyst_agent() -> Agent:
    """문체를 '측정'하는 역할. 창작이 아니므로 temperature 를 낮게 둔다."""
    return Agent(
        role="블로그 문체 분석가",
        goal=(
            "주어진 기존 글에서 재현 가능한 문체 특징을 뽑아내고, "
            "요청 주제와 관련이 깊은 글을 골라낸다."
        ),
        backstory=(
            "당신은 편집자 출신 문체 분석가입니다. 글을 읽고 '좋다/나쁘다'를 "
            "말하는 대신, 다른 사람이 그대로 흉내 낼 수 있을 만큼 구체적인 "
            "규칙으로 옮겨 적는 일을 합니다. '친근한 어투' 같은 뭉뚱그린 표현 "
            "대신 '~습니다체를 쓰되 2~3문단마다 ~죠? 로 독자에게 말을 건다' "
            "처럼 적습니다."
        ),
        llm=build_llm(temperature=0.2),
        allow_delegation=False,
        verbose=False,
    )


def writer_agent() -> Agent:
    """실제 초안을 쓰는 역할. 소스가 무엇이었는지 모른다."""
    return Agent(
        role="기술 블로그 작가",
        goal="주어진 문체 가이드를 지키면서 요청받은 주제의 초안을 마크다운으로 쓴다.",
        backstory=(
            "당신은 개발 팀의 기술 블로그를 대신 써 온 작가입니다. 당신에게 "
            "주어지는 것은 문체 가이드와 글 요청뿐이고, 그 문체가 어디서 왔는지"
            "(로컬 파일인지 velog인지 템플릿인지)는 알 필요도 없고 묻지도 "
            "않습니다. 가이드에 적힌 규칙을 그대로 지키는 것이 당신의 일입니다."
        ),
        llm=build_llm(temperature=0.7),
        allow_delegation=False,
        verbose=False,
    )


def editor_agent() -> Agent:
    """지적만 하는 역할. 재작성 금지가 이 에이전트의 핵심 제약이다.

    LLM 은 자기회귀적으로 매 토큰을 새로 예측한다. 전문을 다시 쓰게 하면
    고쳐달라고 하지 않은 문장까지 함께 바뀌고, 앞 단계에서 맞춰놓은 문체가
    무너진다. 그래서 편집자의 출력은 '위치 / 문제 / 대안' 목록으로 못 박는다.
    최종 반영 여부는 사람이 정한다.
    """
    return Agent(
        role="원고 검토자",
        goal="초안의 오타·사실오류·논리 비약을 찾아 위치와 대안을 목록으로 제시한다.",
        backstory=(
            "당신은 원고를 고쳐주지 않는 검토자입니다. 당신의 일은 문제를 "
            "정확히 짚어 주는 것까지이고, 문장을 다시 쓰는 것은 필자의 몫이라고 "
            "믿습니다. 전체 원고를 다시 써 달라는 요청을 받아도 거절하고 "
            "지적 목록만 냅니다."
        ),
        llm=build_llm(temperature=0.3),
        allow_delegation=False,
        verbose=False,
    )
