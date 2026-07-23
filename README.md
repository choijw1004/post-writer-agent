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

## API 서버

```bash
.venv/bin/uvicorn server.api:app --reload --port 8000
```

문서는 http://localhost:8000/docs.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/api/health` | 상태·모델명 |
| `GET` | `/api/options` | 독자/목적/분량 선택지 (프론트가 하드코딩하지 않게) |
| `POST` | `/api/jobs` | 생성 작업 시작 → `202 {job_id}` |
| `GET` | `/api/jobs/{id}` | 폴링: 진행 이벤트 + 완료 시 결과 |
| `GET` | `/api/jobs/{id}/stream` | SSE: `progress` 이벤트 → `result` 이벤트 |

파이프라인 한 번이 수십 초라 요청을 붙잡지 않고 job 으로 돌린다. CrewAI 호출이
동기 코드여서 백그라운드 스레드에서 실행하고, 진행 상황만 따로 구독한다.
SSE 가 막히는 환경을 대비해 폴링 경로도 함께 열어 둔다.

```bash
curl -X POST localhost:8000/api/jobs -H 'Content-Type: application/json' -d '{
  "source_type": "local", "path": "./sample_posts",
  "topic": "파이썬 타입 힌트 도입기",
  "audience": "동료 개발자", "purpose": "회고", "length": "짧게"
}'
curl -N localhost:8000/api/jobs/<job_id>/stream
```

## 화면 (React)

백엔드를 8000 포트에 띄운 상태에서:

```bash
cd client
npm install
npm run dev        # http://localhost:5173
```

`/api` 는 vite 프록시가 8000 으로 넘긴다. 개발 중에도 같은 오리진이라 CORS 도,
EventSource 의 크로스 오리진 제약도 신경 쓸 일이 없다.

디자인은 토스 방향을 따랐다.

- **한 화면에 한 가지만 묻는다.** 소스 → 주제 → 독자 → 목적 → 분량 5단계.
  선택형은 고르는 즉시 다음으로 넘어간다.
- **여백이 인상의 8할.** 간격은 `StepShell` 한 곳에서만 정한다.
- **색은 파랑 하나.** 주요 버튼과 진행 표시에만 쓴다.
- **진행 표시는 점 3개.** 에이전트 로그를 늘어놓지 않는다.
- **문체 분석 결과는 분석 단계가 끝나는 즉시 뜬다.** 초안을 기다리는 동안
  빈 화면을 보지 않아도 되고, 이 앱의 데모 포인트이기도 하다.
- **토큰 사용량은 결과 화면 하단 접힌 영역.** 발표 때만 펼친다.

## 구조

```
server/
  pipeline.py      run_pipeline() — CLI와 API의 공통 진입점
  agents.py        분석가 / 작가 / 편집자
  tasks.py         Task description (ReAct 절차 명시)
  models.py        StyleGuide, EditReport 등 내부 자료구조
  tokens.py        토큰 계측 + 샘플 토큰 예산
  sources/         소스별 로더 (local_md 구현)
  cli.py           CLI 인터페이스
  api.py           FastAPI 앱 (HTTP 처리만, 생성 로직 없음)
  jobs.py          백그라운드 job 실행·진행 이벤트 수집
  schemas.py       HTTP 경계 전용 요청/응답 스키마
client/
  src/App.jsx      단계 흐름과 상태 (일반적인 useState 방식)
  src/api.js       서버와 이야기하는 유일한 곳 (SSE, 실패 시 폴링)
  src/components/  StepShell, ChoiceList, ProgressDots, StyleGuideCard,
                   ResultView, TokenPanel …
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
- [x] FastAPI로 감싸기 (SSE + 폴링)
- [x] React UI (토스 스타일)
- [ ] velog API 연동
- [ ] 템플릿 경로 (글 없는 사용자)
- [ ] 후속 수정 대화
