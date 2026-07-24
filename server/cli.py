"""CLI 진입점.

    python -m server.cli --path ./sample_posts --topic "FastAPI 의존성 주입"

화면(React)이 붙기 전까지 이 CLI 가 데모 경로다. run_pipeline 을 그대로
호출하므로, 나중에 FastAPI 를 얹어도 이 파일은 바뀌지 않는다.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from server import config, tokens
from server.doc_types import DOC_TYPE_NAMES
from server.models import PipelineResult, ReviewResult, SourceSpec
from server.pipeline import run_pipeline, run_review
from server.sources import VelogError

STAGE_LABEL = {
    "load": "기존 글 로드",
    "analyze": "① 분석가 — 문체 추출",
    "write": "② 작가 — 초안 작성",
    "check": "① 결정적 검사 (토큰 0)",
    "edit": "② 편집자 — 오타·논리",
}


def progress(stage: str, status: str, data: dict | None = None) -> None:
    label = STAGE_LABEL.get(stage, stage)
    if status == "start":
        print(f"  ▶ {label} …", flush=True)
        return

    if stage == "load" and data:
        detail = (
            f"글 {data['found']}편 중 {data['selected']}편 선택"
            f" ({data['sample_tokens']:,} 토큰)"
        )
        print(f"  ✓ {label}: {detail}", flush=True)
        return

    if stage == "analyze" and data and data.get("preset"):
        print("  ✓ 기본 문체 적용 (쓴 글이 없어 분석 생략, 토큰 0)", flush=True)
        return

    print(f"  ✓ {label} 완료", flush=True)


def print_result(result: PipelineResult) -> None:
    sg = result.style_guide

    print("\n" + "=" * 72)
    print("문체 분석 결과")
    print("=" * 72)
    print(sg.to_prompt_block())
    if sg.referenced_posts:
        print(f"- 주제 관련 참고 글: {', '.join(sg.referenced_posts)}")

    print("\n" + "=" * 72)
    print("초안")
    print("=" * 72)
    print(result.draft_markdown)

    print("\n" + "=" * 72)
    print(f"토큰 사용량 (모델: {config.MODEL})")
    print("=" * 72)
    print(f"문체 샘플 {len(result.sample_titles)}편 = {result.sample_tokens:,} 토큰")
    for title in result.sample_titles:
        print(f"  · {title}")
    print()
    print(tokens.format_usage_table(result.usage))


def print_review(result: ReviewResult) -> None:
    print("\n" + "=" * 72)
    print("지적 사항 (글을 고쳐주지는 않습니다)")
    print("=" * 72)

    if not result.notes:
        print("짚을 곳이 없습니다.")
    for i, note in enumerate(result.notes, start=1):
        badge = "자동 검사" if note.source == "auto" else "모델 판단"
        print(f"\n{i}. [{badge} · {note.kind}] {note.location}")
        print(f"   문제: {note.problem}")
        print(f"   대안: {note.suggestion}")

    if result.overall:
        print(f"\n총평: {result.overall}")

    print("\n" + "=" * 72)
    print(f"토큰 사용량 (모델: {config.MODEL})")
    print("=" * 72)
    print(f"자동 검사 {result.auto_count}건은 토큰을 쓰지 않았습니다.")
    print()
    print(tokens.format_usage_table(result.usage))


def run_review_command(args) -> int:
    """--review FILE 로 들어온 글 다듬기."""
    path = Path(args.review).expanduser()
    if not path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {path}", file=sys.stderr)
        return 1

    print(f"검토 대상: {path}")
    print(f"문서 유형: {args.type}\n")

    result = run_review(
        draft=path.read_text(encoding="utf-8"),
        doc_type=args.type,
        on_progress=progress,
    )
    print_review(result)
    return 0


def _configure_logging() -> None:
    """kickoff 실행 로그(cholog.*)를 stderr 로 보이게 한다.

    루트 로거를 건드리지 않으므로 다른 라이브러리 로그는 조용하다.
    """
    logger = logging.getLogger("cholog")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("  %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(
        prog="cholog",
        description="기존 글의 문체를 학습해 초안을 만들거나, 이미 쓴 글을 다듬습니다.",
    )
    parser.add_argument(
        "--review",
        metavar="FILE",
        help="글 다듬기: 검토할 마크다운 파일 (이 옵션을 주면 초안 작성은 건너뜁니다)",
    )
    parser.add_argument(
        "--source", default="local", choices=["local", "velog", "template"]
    )
    parser.add_argument("--path", help="local 소스: 마크다운 폴더 경로")
    parser.add_argument("--username", help="velog 소스: 사용자명 (@ 없이)")
    parser.add_argument("--topic", help="쓸 글의 주제 (초안 작성 시 필수)")
    parser.add_argument(
        "--type",
        default="설명 문서",
        choices=DOC_TYPE_NAMES,
        help="문서 유형 (docs/type.md 의 4종)",
    )
    parser.add_argument("--tone", default="경어체", choices=config.TONES)
    parser.add_argument(
        "--material",
        default="",
        help="글의 재료: 겪은 일·메모·코드 조각 (선택)",
    )
    parser.add_argument(
        "--material-file",
        metavar="FILE",
        help="재료를 파일에서 읽는다 (--material 보다 우선)",
    )
    parser.add_argument("--out", help="초안 마크다운을 저장할 파일 경로")
    args = parser.parse_args(argv)

    # 진입점이 둘이라 여기서 갈린다. 화면의 랜딩 두 갈래와 같은 갈림이다.
    if args.review:
        try:
            return run_review_command(args)
        except ValueError as e:
            print(f"\n오류: {e}", file=sys.stderr)
            return 1

    if not args.topic:
        parser.error("초안 작성에는 --topic 이 필요합니다 (또는 --review 를 쓰세요).")

    source = SourceSpec(type=args.source, path=args.path, username=args.username)

    material = args.material
    if args.material_file:
        material_path = Path(args.material_file).expanduser()
        if not material_path.exists():
            print(f"오류: 재료 파일을 찾을 수 없습니다: {material_path}", file=sys.stderr)
            return 1
        material = material_path.read_text(encoding="utf-8")

    print(f"주제: {args.topic}")
    print(f"문서 유형: {args.type} / 말투: {args.tone}", end="")
    print(f" / 재료: {len(material):,}자" if material else "")
    print()

    try:
        result = run_pipeline(
            source=source,
            topic=args.topic,
            doc_type=args.type,
            tone=args.tone,
            material=material,
            on_progress=progress,
        )
    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        NotImplementedError,
        VelogError,
    ) as e:
        print(f"\n오류: {e}", file=sys.stderr)
        return 1

    print_result(result)

    if args.out:
        out_path = Path(args.out).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result.draft_markdown + "\n", encoding="utf-8")
        print(f"\n초안 저장: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
