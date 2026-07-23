"""CLI 진입점.

    python -m server.cli --path ./sample_posts --topic "FastAPI 의존성 주입"

화면(React)이 붙기 전까지 이 CLI 가 데모 경로다. run_pipeline 을 그대로
호출하므로, 나중에 FastAPI 를 얹어도 이 파일은 바뀌지 않는다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from server import config, tokens
from server.models import PipelineResult, SourceSpec
from server.pipeline import run_pipeline

STAGE_LABEL = {
    "load": "기존 글 로드",
    "analyze": "① 분석가 — 문체 추출",
    "write": "② 작가 — 초안 작성",
    "edit": "③ 편집자 — 검토",
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
    print("편집자 지적 사항 (재작성 아님 — 반영 여부는 사람이 결정)")
    print("=" * 72)
    if result.edit_report.notes:
        for i, note in enumerate(result.edit_report.notes, start=1):
            print(f"\n{i}. [{note.location}]")
            print(f"   문제: {note.problem}")
            print(f"   대안: {note.suggestion}")
    else:
        print("지적 사항 없음")
    if result.edit_report.overall:
        print(f"\n총평: {result.edit_report.overall}")

    print("\n" + "=" * 72)
    print(f"토큰 사용량 (모델: {config.MODEL})")
    print("=" * 72)
    print(f"문체 샘플 {len(result.sample_titles)}편 = {result.sample_tokens:,} 토큰")
    for title in result.sample_titles:
        print(f"  · {title}")
    print()
    print(tokens.format_usage_table(result.usage))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="blog-agent",
        description="기존 글의 문체를 학습해 새 블로그 초안을 생성합니다.",
    )
    parser.add_argument(
        "--source", default="local", choices=["local", "velog", "template"]
    )
    parser.add_argument("--path", help="local 소스: 마크다운 폴더 경로")
    parser.add_argument("--topic", required=True, help="쓸 글의 주제")
    parser.add_argument("--audience", default="주니어 개발자", choices=config.AUDIENCES)
    parser.add_argument("--purpose", default="학습 정리", choices=config.PURPOSES)
    parser.add_argument("--length", default="보통", choices=config.LENGTHS)
    parser.add_argument("--out", help="초안 마크다운을 저장할 파일 경로")
    args = parser.parse_args(argv)

    source = SourceSpec(type=args.source, path=args.path)

    print(f"주제: {args.topic}")
    print(f"독자: {args.audience} / 목적: {args.purpose} / 분량: {args.length}\n")

    try:
        result = run_pipeline(
            source=source,
            topic=args.topic,
            audience=args.audience,
            purpose=args.purpose,
            length=args.length,
            on_progress=progress,
        )
    except (FileNotFoundError, NotADirectoryError, ValueError, NotImplementedError) as e:
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
