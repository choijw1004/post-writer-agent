"""토큰 계측과 예산 관리.

문서의 '반드시 구현할 것' 두 항목이 여기에 걸려 있다.
- 단계별 input/output 토큰과 누적 합계
- 스타일 샘플 개수를 토큰 예산 기준으로 제한
"""

from __future__ import annotations

import tiktoken

from server import config
from server.models import Post, StageUsage

_encoding = None


def encoding() -> tiktoken.Encoding:
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding(config.ENCODING_NAME)
    return _encoding


def count_tokens(text: str) -> int:
    return len(encoding().encode(text))


def truncate_to_tokens(text: str, limit: int) -> str:
    """토큰 기준으로 자른다. 글자 수로 자르면 한글/영어가 다르게 잘린다."""
    enc = encoding()
    ids = enc.encode(text)
    if len(ids) <= limit:
        return text
    return enc.decode(ids[:limit]) + "\n\n…(이하 생략)"


def select_style_samples(
    posts: list[Post],
    budget: int = config.STYLE_SAMPLE_TOKEN_BUDGET,
    per_post_cap: int = config.PER_POST_TOKEN_CAP,
    max_posts: int = config.MAX_STYLE_SAMPLES,
) -> tuple[list[Post], int]:
    """토큰 예산 안에서 문체 샘플을 고른다.

    글을 몇 편 넣을지는 감이 아니라 예산으로 정한다. 컨텍스트 윈도우는
    유한하고, 넣은 토큰 전부가 Self-Attention 연산 대상이 되기 때문에
    "많이 넣을수록 좋다"가 성립하지 않는다.

    Returns:
        (예산 안에 들어온 샘플 목록, 실제 사용 토큰 수)
    """
    selected: list[Post] = []
    used = 0

    # 긴 글일수록 문체 정보가 풍부하다고 보고 긴 순서로 채운다.
    for post in sorted(posts, key=lambda p: len(p.body), reverse=True):
        if len(selected) >= max_posts:
            break
        excerpt = truncate_to_tokens(post.body, per_post_cap)
        cost = count_tokens(excerpt)
        if used + cost > budget:
            continue  # 이 글은 건너뛰고, 더 짧은 글로 예산을 채워본다
        selected.append(Post(title=post.title, body=excerpt, origin=post.origin))
        used += cost

    return selected, used


def usage_from_crew_output(stage: str, token_usage, seconds: float = 0.0) -> StageUsage:
    """CrewAI 의 UsageMetrics 를 우리 자료구조로 옮긴다."""
    return StageUsage(
        stage=stage,
        prompt_tokens=getattr(token_usage, "prompt_tokens", 0) or 0,
        completion_tokens=getattr(token_usage, "completion_tokens", 0) or 0,
        total_tokens=getattr(token_usage, "total_tokens", 0) or 0,
        requests=getattr(token_usage, "successful_requests", 0) or 0,
        seconds=round(seconds, 2),
    )


def format_usage_table(usages: list[StageUsage]) -> str:
    """CLI 출력용 표. 발표 때 그대로 보여줄 수 있게."""
    header = f"{'단계':<10}{'input':>10}{'output':>10}{'합계':>10}{'호출':>7}{'시간(s)':>10}"
    lines = [header, "─" * len(header) * 2]
    for u in usages:
        lines.append(
            f"{u.stage:<10}{u.prompt_tokens:>10,}{u.completion_tokens:>10,}"
            f"{u.total_tokens:>10,}{u.requests:>7}{u.seconds:>10.2f}"
        )
    total_in = sum(u.prompt_tokens for u in usages)
    total_out = sum(u.completion_tokens for u in usages)
    total = sum(u.total_tokens for u in usages)
    total_req = sum(u.requests for u in usages)
    total_sec = sum(u.seconds for u in usages)
    lines.append("─" * len(header) * 2)
    lines.append(
        f"{'누적':<10}{total_in:>10,}{total_out:>10,}{total:>10,}"
        f"{total_req:>7}{total_sec:>10.2f}"
    )
    return "\n".join(lines)
