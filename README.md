# blog-agent

기존 블로그 글의 문체를 분석해 새 글 초안을 생성하는 에이전트.
분석가 → 작가 → 편집자 3단계로 나눈 CrewAI 파이프라인이다.

요구사항 문서는 `docs/docs.md`.

## 설치

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
```

## 실행

```bash
.venv/bin/python -m server.cli \
  --path ./sample_posts \
  --topic "FastAPI 의존성 주입으로 DB 세션 관리하기" \
  --audience "주니어 개발자" \
  --purpose "학습 정리" \
  --length "짧게" \
  --out ./out/draft.md
```

| 옵션 | 값 |
|---|---|
| `--source` | `local` (구현됨) / `velog` / `template` (미구현) |
| `--path` | local 소스의 마크다운 폴더 |
| `--audience` | 주니어 개발자 / 동료 개발자 / 비개발자 / 일반 독자 |
| `--purpose` | 학습 정리 / 트러블슈팅 공유 / 회고 / 튜토리얼 |
| `--length` | 짧게 / 보통 / 길게 |

한/영 토큰 비교 실험 (발표자료용):

```bash
.venv/bin/python -m scripts.token_compare
```

## 구조

```
server/
  pipeline.py      run_pipeline() — CLI와 (추후) FastAPI의 공통 진입점
  agents.py        분석가 / 작가 / 편집자
  tasks.py         Task description (ReAct 절차 명시)
  models.py        StyleGuide, EditReport 등 자료구조
  tokens.py        토큰 계측 + 샘플 토큰 예산
  sources/         소스별 로더 (local_md 구현)
  cli.py           CLI 인터페이스
scripts/
  token_compare.py 한/영 토큰 수 비교 실험
sample_posts/      데모용 마크다운 3편
```

## 설계 메모 (수업 개념 연결)

- **토큰화** — 문체 샘플을 원문 그대로 넘기지 않고 `StyleGuide` 로 압축한다.
  한국어는 같은 의미에 영어보다 토큰이 1.6배가량 더 들기 때문에
  (`scripts/token_compare.py` 로 측정) 원문 적재는 비싸다.
- **컨텍스트 윈도우** — 샘플 개수를 '몇 편'이 아니라 '몇 토큰'으로 제한한다.
  `config.STYLE_SAMPLE_TOKEN_BUDGET`, `tokens.select_style_samples()`.
- **Self-Attention** — 한 프롬프트에 분석·작성·검토를 몰아넣지 않고 3단계로
  쪼갰다. 시퀀스 길이에 대해 비용이 N² 로 늘고, 길수록 지시가 희석된다.
- **자기회귀 생성** — 편집자에게 전문 재작성을 금지하고 `위치/문제/대안`
  목록만 내게 한다. 매 토큰을 새로 예측하므로 전문을 다시 쓰게 하면 고치라고
  하지 않은 문장까지 바뀌고 앞 단계에서 맞춘 문체가 무너진다.
  (`agents.editor_agent`, `tasks.editing_task`)

단계별 토큰 사용량은 실행 결과 하단에 표로 출력된다.

## 진행 상황

- [x] 로컬 md 로드 → 문체 분석 → 초안 생성 → 편집 (CLI 완주)
- [x] 토큰 측정
- [ ] FastAPI로 감싸기
- [ ] React UI (토스 스타일)
- [ ] velog API 연동
- [ ] 템플릿 경로 (글 없는 사용자)
- [ ] 후속 수정 대화
