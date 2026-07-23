"""기존 글 소스. 어떤 소스든 list[Post] 로 수렴한다."""

from server.models import Post, SourceSpec
from server.sources.local_md import load_local_posts, parse_markdown
from server.sources.velog import VelogError, load_velog_posts


def load_posts(source: SourceSpec) -> list[Post]:
    """소스 명세를 받아 글 목록을 돌려준다.

    이 함수가 소스 분기를 흡수하는 유일한 지점이다. 뒤쪽 단계(분석가·작가·
    편집자)는 소스가 무엇이었는지 알지 못한다.
    """
    if source.type == "local":
        if not source.path:
            raise ValueError("local 소스는 path(마크다운 폴더 경로)가 필요합니다.")
        return load_local_posts(source.path)

    if source.type == "upload":
        # 브라우저가 폴더에서 읽어 이미 Post 로 만들어 보낸 경우.
        # 파싱은 api 계층에서 parse_markdown 으로 끝내고 온다.
        if not source.posts:
            raise ValueError("업로드된 마크다운 글이 없습니다.")
        return source.posts

    if source.type == "velog":
        if not source.username:
            raise ValueError("velog 소스는 username 이 필요합니다.")
        return load_velog_posts(source.username)

    if source.type == "template":
        # 구현 우선순위 6번.
        raise NotImplementedError(
            "템플릿 소스는 아직 미구현입니다. --source local 로 실행하세요."
        )

    raise ValueError(f"알 수 없는 소스 타입: {source.type}")


__all__ = [
    "load_posts",
    "load_local_posts",
    "load_velog_posts",
    "parse_markdown",
    "VelogError",
]
