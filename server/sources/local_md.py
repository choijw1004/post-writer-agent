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
        title, body = _split_frontmatter(raw)

        if not title:
            h1 = _H1.search(body)
            title = h1.group(1).strip() if h1 else path.stem

        body = body.strip()
        if not body:
            continue  # 빈 파일은 문체 정보가 없다

        posts.append(Post(title=title, body=body, origin=str(path)))

    if not posts:
        raise ValueError(f"{root} 안에서 읽을 수 있는 마크다운 글을 찾지 못했습니다.")

    return posts
