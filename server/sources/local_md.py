"""로컬 마크다운 폴더 로더 (GitHub Pages 블로그의 _posts 같은 경로)."""

from __future__ import annotations

import re
from pathlib import Path

from server.models import Post

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TITLE_IN_FM = re.compile(r"^title\s*:\s*(.+)$", re.MULTILINE)
_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _split_frontmatter(raw: str) -> tuple[str | None, str]:
    """YAML 프론트매터를 떼어내고 (title, body) 를 돌려준다."""
    match = _FRONTMATTER.match(raw)
    if not match:
        return None, raw

    fm, body = match.group(1), raw[match.end() :]
    title_match = _TITLE_IN_FM.search(fm)
    title = title_match.group(1).strip().strip("\"'") if title_match else None
    return title, body


def parse_markdown(name: str, raw: str, origin: str | None = None) -> Post | None:
    """마크다운 원문 하나를 Post 로 만든다.

    제목은 프론트매터 title → 첫 h1 → 파일명 순으로 찾는다.
    본문이 비어 있으면 문체 정보가 없으므로 None 을 돌려준다.

    파일을 직접 읽는 경로(load_local_posts)와 브라우저에서 올라온 내용을
    받는 경로가 이 함수를 공유한다. 제목 규칙이 갈라지지 않게 하려는 것이다.
    """
    title, body = _split_frontmatter(raw)

    if not title:
        h1 = _H1.search(body)
        title = h1.group(1).strip() if h1 else Path(name).stem

    body = body.strip()
    if not body:
        return None

    return Post(title=title, body=body, origin=origin or name)


def load_local_posts(directory: str | Path) -> list[Post]:
    """폴더 안의 .md / .markdown 파일을 모두 읽는다.

    제목은 프론트매터 title → 첫 h1 → 파일명 순으로 찾는다.
    """
    root = Path(directory).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"경로를 찾을 수 없습니다: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"폴더가 아닙니다: {root}")

    posts: list[Post] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue

        raw = path.read_text(encoding="utf-8")
        post = parse_markdown(path.name, raw, origin=str(path))
        if post:
            posts.append(post)

    if not posts:
        raise ValueError(f"{root} 안에서 읽을 수 있는 마크다운 글을 찾지 못했습니다.")

    return posts
