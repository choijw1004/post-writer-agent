"""결정적 검사.

LLM 을 부르지 않고 코드로 확실히 판정되는 것만 잡는다. 토큰이 들지 않고,
같은 글에 대해 항상 같은 결과가 나온다.

이 층을 따로 두는 이유가 있다. 자기회귀 생성 모델에게 자기 출력을 검증시키는
것은 같은 분포에서 다시 뽑는 것과 같다. 존재하지 않는 코드를 그럴듯하다고
판단해 써낸 모델이, 같은 코드를 그럴듯하지 않다고 판단할 이유가 없다.
그래서 기계적으로 판정 가능한 것은 모델에게 묻지 않고 여기서 끝낸다.

여기서 보는 것은 전부 '글 안'이다. 바깥 사실(존재하는 API 인지, 수치가 맞는지)은
검사하지 않는다.
"""

from __future__ import annotations

import ast
import re

from server.models import ReviewNote

# ```python 처럼 언어 태그가 붙은 코드펜스와 그 본문
_FENCE = re.compile(r"^```([^\n`]*)\n(.*?)^```", re.MULTILINE | re.DOTALL)
_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")

_PYTHON_TAGS = {"python", "py", "python3"}


def _strip_code_blocks(markdown: str) -> str:
    """코드 안의 내용이 본문 검사에 섞이지 않게 걷어낸다."""
    return _FENCE.sub("", markdown)


def count_subheadings(markdown: str) -> int:
    """소제목(##, ###) 개수.

    작가가 최소 개수 지시를 지켰는지는 모델에게 다시 묻지 않고 여기서 센다.
    모자라면 pipeline 이 보강 Task 를 한 번 더 돌린다.
    """
    text = _strip_code_blocks(markdown)
    return sum(1 for m in _HEADING.finditer(text) if len(m.group(1)) in (2, 3))


def check_code_fences(markdown: str) -> list[ReviewNote]:
    """코드펜스의 언어 태그와, 파이썬 코드의 문법을 본다."""
    notes: list[ReviewNote] = []

    for index, match in enumerate(_FENCE.finditer(markdown), start=1):
        tag = match.group(1).strip().lower()
        body = match.group(2)

        if not tag:
            notes.append(
                ReviewNote(
                    kind="형식",
                    source="auto",
                    location=f"{index}번째 코드블록",
                    problem="언어 태그가 없어 문법 강조가 되지 않습니다.",
                    suggestion="``` 뒤에 python, bash 처럼 언어를 적어주세요.",
                )
            )
            continue

        if tag not in _PYTHON_TAGS:
            continue

        try:
            ast.parse(body)
        except SyntaxError as exc:
            # 발췌 코드는 원래 조각인 경우가 많아서, 문법이 깨진 위치만 알린다.
            notes.append(
                ReviewNote(
                    kind="형식",
                    source="auto",
                    location=f"{index}번째 코드블록 {exc.lineno}번째 줄",
                    problem=f"파이썬 문법이 성립하지 않습니다: {exc.msg}",
                    suggestion=(
                        "코드를 그대로 실행할 수 있는 형태로 고치거나, "
                        "일부 발췌라면 생략 표시를 넣어주세요."
                    ),
                )
            )

    return notes


def check_heading_levels(markdown: str) -> list[ReviewNote]:
    """제목 단계가 건너뛰는지 본다 (h1 다음에 바로 h3 등)."""
    notes: list[ReviewNote] = []
    headings = _HEADING.findall(_strip_code_blocks(markdown))

    top_level = [text for marks, text in headings if len(marks) == 1]
    if len(top_level) > 1:
        notes.append(
            ReviewNote(
                kind="형식",
                source="auto",
                location="문서 전체",
                problem=f"최상위 제목(#)이 {len(top_level)}개입니다.",
                suggestion="글 제목은 하나만 두고 나머지는 ## 이하로 낮춰주세요.",
            )
        )

    previous = 0
    for marks, text in headings:
        level = len(marks)
        if previous and level > previous + 1:
            notes.append(
                ReviewNote(
                    kind="형식",
                    source="auto",
                    location=f"'{text.strip()}'",
                    problem=f"제목 단계가 h{previous} 에서 h{level} 로 건너뜁니다.",
                    suggestion=f"h{previous + 1} 로 낮추거나 중간 단계를 넣어주세요.",
                )
            )
        previous = level

    return notes


def check_links(markdown: str) -> list[ReviewNote]:
    """마크다운 링크의 주소가 비었거나 자리표시자로 남아 있는지 본다."""
    notes: list[ReviewNote] = []

    for text, url in _LINK.findall(_strip_code_blocks(markdown)):
        target = url.strip()
        broken = (
            not target
            or target in {"#", "url", "URL", "링크"}
            or target.startswith("http://example.com")
            or target.startswith("https://example.com")
        )
        if broken:
            notes.append(
                ReviewNote(
                    kind="형식",
                    source="auto",
                    location=f"링크 '{text or '(빈 문구)'}'",
                    problem=f"주소가 비었거나 자리표시자입니다: '{target}'",
                    suggestion="실제 주소로 바꾸거나 링크를 지워주세요.",
                )
            )

    return notes


def check_repeated_sentences(markdown: str) -> list[ReviewNote]:
    """같은 문장이 반복되는지 본다.

    자기회귀 생성은 같은 표현으로 되돌아오는 경향이 있어서, 긴 글일수록
    똑같은 문장이 두 번 나오는 일이 실제로 생긴다.
    """
    # 제목 줄을 먼저 걷어낸다. 제목은 마침표로 끝나지 않아서 그대로 두면
    # 뒤 문장과 한 덩어리로 붙어버리고, 그 덩어리는 다른 곳의 같은 문장과
    # 일치하지 않는다.
    body = _HEADING.sub("", _strip_code_blocks(markdown))
    sentences = [s.strip() for s in re.split(r"(?<=[.!?다요])\s+", body)]

    seen: dict[str, int] = {}
    notes: list[ReviewNote] = []
    for sentence in sentences:
        # 짧은 문장("그렇습니다." 등)은 우연히 겹칠 수 있으므로 길이로 거른다.
        # 한국어는 같은 뜻을 영어보다 짧은 글자 수로 쓰기 때문에 기준을
        # 너무 높이면(25자 이상) 실제 반복을 놓친다.
        if len(sentence) < 18:
            continue
        seen[sentence] = seen.get(sentence, 0) + 1

    for sentence, count in seen.items():
        if count > 1:
            notes.append(
                ReviewNote(
                    kind="형식",
                    source="auto",
                    location=f"'{sentence[:30]}…'",
                    problem=f"같은 문장이 {count}번 나옵니다.",
                    suggestion="한쪽을 지우거나 다르게 표현해주세요.",
                )
            )

    return notes


_CODE_HINT = ("코드", "```", "코드블록")
_SYNTAX_HINT = ("문법", "구문", "콜론", "괄호", "들여쓰기", "syntax")


def drop_overlapping(
    auto_notes: list[ReviewNote], model_notes: list[ReviewNote]
) -> list[ReviewNote]:
    """자동 검사가 이미 잡은 것을 모델이 또 지적하면 버린다.

    프롬프트에서 "코드 문법은 보지 마라"고 막고, 이미 찾은 목록까지 넘겨도
    모델은 눈앞의 깨진 코드를 그냥 지나치지 못한다. 실제로 gpt-4o-mini 는
    양쪽을 다 해도 같은 지적을 반복했다.

    지시를 더 세게 쓰는 대신 여기서 거른다. 모델이 지시를 지킬 것이라는
    가정 위에 결과 품질을 올려두지 않으려는 것이다.
    """
    has_auto_code_finding = any("코드블록" in note.location for note in auto_notes)
    if not has_auto_code_finding:
        return model_notes

    kept = []
    for note in model_notes:
        text = f"{note.location} {note.problem}"
        about_code = any(hint in text for hint in _CODE_HINT)
        about_syntax = any(hint in text.lower() for hint in _SYNTAX_HINT)
        if about_code and about_syntax:
            continue  # 자동 검사가 같은 코드블록을 이미 확정 판정했다
        kept.append(note)

    return kept


def run_checks(markdown: str) -> list[ReviewNote]:
    """결정적 검사를 모두 돌린다. LLM 을 부르지 않으므로 토큰이 0이다."""
    notes: list[ReviewNote] = []
    for check in (
        check_code_fences,
        check_heading_levels,
        check_links,
        check_repeated_sentences,
    ):
        notes.extend(check(markdown))
    return notes
