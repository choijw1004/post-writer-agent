"""velog 소스.

velog 는 공개 API 를 제공하지 않는다. 여기서 쓰는 GraphQL 엔드포인트는 웹
클라이언트가 쓰는 것을 그대로 부르는 것이라, 스키마가 예고 없이 바뀔 수 있다.
실제로 인자 형태가 한 번 바뀌었다(플랫 인자 -> input 객체).

그래서 두 가지를 지킨다.
- 실패했을 때 "velog 가 바뀌었다"는 것을 바로 알 수 있게 메시지를 남긴다.
  데모 중에 원인을 찾느라 헤매지 않기 위해서다.
- 이 모듈이 죽어도 로컬 md 경로는 영향받지 않는다. 소스 분기는
  sources/__init__.py 한 곳에만 있다.
"""

from __future__ import annotations

import httpx

from server import config
from server.models import Post

_POSTS_QUERY = """
query Posts($input: GetPostsInput!) {
  posts(input: $input) {
    id
    title
    url_slug
    released_at
  }
}
"""

_POST_QUERY = """
query Post($input: ReadPostInput!) {
  post(input: $input) {
    id
    title
    body
  }
}
"""


class VelogError(RuntimeError):
    """velog 조회 실패. 사용자에게 그대로 보여줄 수 있는 문장을 담는다."""


def _call(client: httpx.Client, query: str, variables: dict) -> dict:
    try:
        res = client.post(
            config.VELOG_API_URL,
            json={"query": query, "variables": variables},
        )
        res.raise_for_status()
        payload = res.json()
    except httpx.TimeoutException as exc:
        raise VelogError("velog 응답이 너무 느립니다. 잠시 후 다시 시도해 주세요.") from exc
    except httpx.HTTPError as exc:
        raise VelogError(f"velog 에 연결하지 못했습니다: {exc}") from exc
    except ValueError as exc:
        raise VelogError("velog 가 JSON 이 아닌 응답을 보냈습니다.") from exc

    if payload.get("errors"):
        message = payload["errors"][0].get("message", "알 수 없는 오류")
        # 비공식 API 라 스키마가 바뀌면 여기로 떨어진다.
        raise VelogError(
            f"velog GraphQL 오류: {message}. "
            "비공식 API 라 스키마가 바뀌었을 수 있습니다 "
            "(server/sources/velog.py 의 쿼리를 확인하세요)."
        )

    data = payload.get("data")
    if data is None:
        raise VelogError("velog 응답에 data 가 없습니다.")
    return data


def load_velog_posts(
    username: str,
    limit: int = config.VELOG_FETCH_LIMIT,
) -> list[Post]:
    """velog 사용자의 최근 글을 본문까지 읽어온다.

    목록과 본문이 별도 쿼리라 글 수만큼 요청이 나간다. 그래서 애초에 최근
    limit 편만 가져온다. 어차피 뒤에서 토큰 예산으로 더 줄어든다.
    """
    username = username.strip().lstrip("@")
    if not username:
        raise VelogError("velog 사용자명이 비어 있습니다.")

    with httpx.Client(timeout=config.VELOG_TIMEOUT) as client:
        listing = _call(
            client,
            _POSTS_QUERY,
            {"input": {"username": username, "limit": limit}},
        )
        entries = listing.get("posts") or []
        if not entries:
            raise VelogError(
                f"@{username} 의 글을 찾지 못했습니다. 사용자명을 확인해 주세요."
            )

        posts: list[Post] = []
        for entry in entries:
            detail = _call(client, _POST_QUERY, {"input": {"id": entry["id"]}})
            body = ((detail.get("post") or {}).get("body") or "").strip()
            if not body:
                continue  # 비공개거나 본문이 빈 글은 문체 정보가 없다

            posts.append(
                Post(
                    title=entry.get("title") or entry.get("url_slug") or "제목 없음",
                    body=body,
                    origin=f"https://velog.io/@{username}/{entry.get('url_slug', '')}",
                )
            )

    if not posts:
        raise VelogError(f"@{username} 에서 본문을 읽을 수 있는 글이 없습니다.")

    return posts
