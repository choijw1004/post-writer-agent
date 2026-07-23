"""한/영 토큰 수 비교 실험 (발표자료용 별도 스크립트).

    python -m scripts.token_compare

같은 뜻의 문장을 한국어와 영어로 각각 토큰화해서 비교한다. 이 실험이 이
프로젝트 설계에 미친 영향:

- 한국어는 같은 의미를 담는 데 영어보다 토큰이 더 든다. BPE 어휘가 영어
  중심으로 만들어져 한글은 여러 조각으로 쪼개지기 때문이다.
- 그래서 문체 샘플을 원문 그대로 프롬프트에 싣는 방식은 한국어 블로그에서
  특히 비싸다. server/models.py 의 StyleGuide 로 압축해 넘기는 설계가
  여기서 나왔다.
- 샘플 개수도 '몇 편'이 아니라 '몇 토큰'으로 제한한다
  (server/config.py STYLE_SAMPLE_TOKEN_BUDGET).
"""

from __future__ import annotations

import tiktoken

from server import config

PAIRS: list[tuple[str, str]] = [
    (
        "이 함수는 사용자 입력을 검증한 뒤 데이터베이스에 저장합니다.",
        "This function validates the user input and then saves it to the database.",
    ),
    (
        "비동기 처리를 도입했더니 응답 시간이 절반으로 줄었습니다.",
        "Introducing async processing cut the response time in half.",
    ),
    (
        "문단은 세 문장 안팎으로 짧게 유지하고, 소제목은 명사형으로 답니다.",
        "Keep paragraphs to about three sentences and write headings as noun phrases.",
    ),
    (
        "토큰화 방식 때문에 같은 의미라도 언어에 따라 비용이 달라집니다.",
        "Because of tokenization, the same meaning costs differently across languages.",
    ),
]


def main() -> None:
    enc = tiktoken.get_encoding(config.ENCODING_NAME)

    print(f"인코딩: {config.ENCODING_NAME} (모델: {config.MODEL})\n")
    header = f"{'#':<3}{'한국어':>8}{'영어':>8}{'배율':>8}   문장"
    print(header)
    print("─" * 80)

    ko_total = en_total = 0
    for i, (ko, en) in enumerate(PAIRS, start=1):
        ko_n = len(enc.encode(ko))
        en_n = len(enc.encode(en))
        ko_total += ko_n
        en_total += en_n
        print(f"{i:<3}{ko_n:>8}{en_n:>8}{ko_n / en_n:>8.2f}x   {ko}")

    print("─" * 80)
    print(f"{'합계':<3}{ko_total:>8}{en_total:>8}{ko_total / en_total:>8.2f}x")

    print("\n[토큰 분해 예시]")
    sample = PAIRS[0][0]
    pieces = [enc.decode([t]) for t in enc.encode(sample)]
    print(f"  원문: {sample}")
    print(f"  분해: {' | '.join(pieces)}")
    print(f"  → 글자 {len(sample)}자가 토큰 {len(pieces)}개로 쪼개졌다.")

    print("\n[설계에 미친 영향]")
    print(f"  · 문체 샘플 토큰 예산: {config.STYLE_SAMPLE_TOKEN_BUDGET:,} 토큰")
    print(f"  · 글 1편당 발췌 상한: {config.PER_POST_TOKEN_CAP:,} 토큰")
    print(f"  · 최대 샘플 편수: {config.MAX_STYLE_SAMPLES}편")
    print("  · 원문 대신 StyleGuide 로 압축해 작가에게 전달")


if __name__ == "__main__":
    main()
