<p align="center">
  <h1 align="center">草綠 초록 (CHO-LOG)</h1>
  <p align="center">
    <strong>내 문체 그대로, 다음 글의 초안부터 퇴고까지</strong>
    <br />
    기존 글에서 문체를 추출해 새로운 기술 블로그 초안을 작성하고,
    <br />
    작성한 글의 오탈자와 논리 문제를 짚어주는 기술 글쓰기 에이전트
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.11x-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/CrewAI-1.15-FF5A50?style=flat-square" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/OpenAI-gpt--4o-412991?style=flat-square&logo=openai&logoColor=white" />
</p>

![alt text](/images/image.png)

---

## Overview

초록(CHO-LOG)은 개발자가 자신의 경험과 문체를 유지한 채 기술 블로그를 작성할 수 있도록 돕는 글쓰기 에이전트입니다.

기술 블로그를 작성하려는 개발자는 다음과 같은 어려움을 겪습니다.

- 무엇부터 써야 할지 막막합니다.
- 개발 경험을 문제·해결·회고의 흐름으로 구조화하기 어렵습니다.
- 생성형 AI를 사용하면 기존에 작성한 글과 다른 획일적인 문체가 만들어집니다.
- 작성한 글의 오탈자나 논리적 비약을 스스로 발견하기 어렵습니다.

초록은 이러한 문제를 해결하기 위해 두 가지 기능을 제공합니다.

1. **초안 작성**  
   기존 기술 블로그에서 문체 특징을 추출하고, 사용자가 입력한 주제와 글감을 바탕으로 새로운 글의 초안을 작성합니다.

2. **퇴고**  
   사용자가 작성한 글에서 오탈자, 어색한 표현, 설명 부족, 논리적 비약을 찾아 위치와 수정 방향을 제시합니다.

초록은 글 전체를 대신 작성하거나 일방적으로 수정하는 도구가 아닙니다.  
마지막 수정과 판단은 사용자에게 남겨 두어, 완성된 글이 끝까지 사용자의 글로 유지되도록 설계했습니다.

> **개발 기간**: 2026.07  
> **팀 구성**: 3명  
> **담당 역할**: PM · Frontend · Backend

---

## Key Features

### 1. 개인 문체 분석

마크다운 폴더 또는 Velog에 작성된 기존 글을 불러와 다음과 같은 문체 특징을 분석합니다.

- 어투와 종결어미
- 문장 길이와 문단 호흡
- 설명 방식
- 소제목 구성 방식
- 기술 용어 사용 방식
- 독자에게 말을 거는 방식

분석 결과는 원문이 아닌 구조화된 `StyleGuide`로 압축되어 초안 작성 단계에 전달됩니다.

### 2. 재료 기반 초안 작성

사용자가 입력한 다음 정보를 바탕으로 기술 블로그 초안을 작성합니다.

- 글의 주제
- 실제로 겪은 문제
- 수치와 측정 결과
- 에러 메시지
- 코드 조각
- 해결 과정과 회고

단순한 기술 설명이 아니라 사용자의 실제 경험이 드러나는 글을 만드는 것을 목표로 합니다.

### 3. 문서 유형별 구조 제공

글의 목적에 따라 네 가지 문서 유형을 선택할 수 있습니다.

| 문서 유형 | 사용 목적 |
|---|---|
| 학습 중심 문서 | 새로운 기술이나 도구를 학습한 과정을 정리할 때 |
| 문제 해결 문서 | 특정 문제의 원인과 해결 과정을 기록할 때 |
| 참조 문서 | 기능, 명령어, API 사용법을 빠르게 확인할 수 있도록 정리할 때 |
| 설명 문서 | 개념, 원리, 등장 배경을 깊이 설명할 때 |

선택한 유형에 따라 글의 구성과 강조되는 내용이 달라집니다.

### 4. 문체가 없는 사용자 지원

기존에 작성한 기술 블로그가 없는 사용자도 기본 문체 프리셋을 활용해 글쓰기를 시작할 수 있습니다.

이 경우 문체 분석 단계를 생략하고, 읽기 쉬운 기본 기술 문서 스타일을 적용합니다.

### 5. 퇴고 결과 제공

퇴고 기능은 사용자의 원문을 직접 재작성하지 않고, 수정이 필요한 부분을 목록으로 제공합니다.

각 지적에는 다음 정보가 포함됩니다.

- 문제가 발견된 위치
- 문제 유형
- 문제가 되는 이유
- 권장 수정 방향
- 판정 주체: 코드 검사 또는 AI 모델

주요 검사 항목은 다음과 같습니다.

- 맞춤법과 오탈자
- 영문 표기 오류
- 어색한 문장 연결
- 설명이 부족한 주장
- 근거 없는 결론
- 문단 간 논리적 비약
- 제목과 본문의 구조 문제

### 6. 토큰 사용량 확인

문체 분석, 초안 작성, 보강, 퇴고 등 각 단계에서 사용된 토큰 수를 기록해 사용자에게 제공합니다.

이를 통해 어느 단계에서 비용이 발생했는지 확인할 수 있습니다.

---

## Service Flow

### 초안 작성

```text
문체 소스 선택
      ↓
기존 글 수집 및 파싱
      ↓
문체 분석·StyleGuide 생성
      ↓
주제 입력
      ↓
글감 입력
      ↓
문서 유형 선택
      ↓
말투 선택
      ↓
초안 작성
      ↓
구조 검증 및 보강
      ↓
최종 마크다운 초안
```

문체 소스는 다음 중 하나를 선택할 수 있습니다.

- 로컬 마크다운 폴더
- 마크다운 파일 업로드
- Velog 사용자 글
- 기본 문체 사용

### 퇴고

```text
마크다운 원문 입력
      ↓
문서 유형 선택
      ↓
결정적 코드 검사
      ↓
편집자 에이전트 검토
      ↓
중복 지적 제거
      ↓
오탈자·논리 문제 목록 제공
```

---

## Agent Architecture

![alt text](/images/image-1.png)

초록은 분석가, 작가, 편집자의 역할을 분리한 멀티 에이전트 구조로 구성되어 있습니다.

### Analyst Agent

기존 글에서 반복적으로 나타나는 문체 특징을 분석합니다.

- 역할: 문체 분석가
- 입력: 사용자의 기존 기술 블로그
- 출력: 구조화된 `StyleGuide`
- Temperature: `0.2`

창작이 아니라 특징을 측정하고 정리하는 역할이므로 낮은 Temperature를 사용합니다.

### Writer Agent

분석된 문체와 사용자가 입력한 주제·글감을 바탕으로 기술 블로그 초안을 작성합니다.

- 역할: 기술 블로그 작가
- 입력: `StyleGuide`, 문서 유형, 주제, 글감, 말투
- 출력: 마크다운 초안
- Temperature: `0.7`

Writer Agent는 기존 글의 원문이나 원문의 출처를 직접 전달받지 않습니다.  
분석가가 생성한 문체 규칙만 전달받아 새로운 글을 작성합니다.

### Editor Agent

사용자가 작성한 원문을 직접 고치지 않고, 문제가 있는 위치와 수정 방향을 제공합니다.

- 역할: 원고 검토자
- 입력: 사용자의 원문, 문서 유형, 코드 검사 결과
- 출력: `EditReport`
- Temperature: `0.3`

전체 글을 다시 작성하지 않도록 제한하고, 오탈자·사실 오류·논리적 비약을 지적 목록으로만 제공합니다.

### Deterministic Check Layer

모델을 사용하지 않아도 판단할 수 있는 항목은 Python 코드로 먼저 검사합니다.

- 마크다운 제목 단계
- 코드 블록 문법
- 링크 형식
- 소제목 개수
- 반복된 제목
- 기본 표기 오류

코드 검사 결과와 모델 검사 결과는 각각 `auto`, `model`로 구분됩니다.

---

## Architecture Principles

### 원문과 작성 에이전트의 분리

기존 글의 원문은 Writer Agent에게 직접 전달되지 않습니다.

```text
기존 글
  ↓
Analyst Agent
  ↓
StyleGuide
  ↓
Writer Agent
  ↓
새로운 초안
```

이를 통해 다음 효과를 얻습니다.

- 기존 글의 문장을 그대로 복사할 가능성 감소
- 입력 글이 많아져도 Writer의 프롬프트 크기 증가 방지
- 데이터 출처와 초안 작성 역할 분리
- 문체 규칙을 재사용할 수 있는 구조 확보

### 역할별 책임 분리

분석, 작성, 검토를 하나의 프롬프트에서 처리하지 않고 역할별로 분리했습니다.

각 에이전트가 하나의 명확한 책임만 수행하도록 하여 출력의 일관성과 유지보수성을 높였습니다.

### 사용자 원문 보존

퇴고 과정에서 모델이 사용자의 글을 임의로 다시 작성하지 못하도록 제한했습니다.

초안의 구조를 보강할 때도 기존 본문을 유지하고 필요한 절만 추가합니다.

---

## Tech Stack

### Backend

![Python 3.12](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-FF5A50?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

### Frontend

![React 19](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key

### Installation

```bash
git clone <repository-url>
cd <repository-directory>
```

#### Backend

```bash
python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

echo "OPENAI_API_KEY=sk-..." > .env

uvicorn server.api:app --reload --port 8000
```

Windows 환경에서는 다음 명령으로 가상환경을 활성화합니다.

```bash
.venv\Scripts\activate
```

#### Frontend

```bash
cd client
npm install
npm run dev
```

### Local URLs

| Service | URL |
|---|---|
| Web | http://localhost:5173 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

브라우저에서 `http://localhost:5173`에 접속해 서비스를 시작합니다.

---

## CLI

### 초안 작성

```bash
.venv/bin/python -m server.cli \
  --path ./sample_posts \
  --topic "도커 빌드 8분을 40초로 줄인 캐시 최적화" \
  --type "문제 해결 문서" \
  --tone "구어체" \
  --material-file ./메모.md \
  --out ./out/draft.md
```

### 퇴고

```bash
.venv/bin/python -m server.cli \
  --review ./out/draft.md \
  --type "설명 문서"
```

---

## API Specification

### 초안 작성 요청

기존 글의 문체를 분석하고 새로운 기술 블로그 초안을 생성합니다.

작업 시간이 길어질 수 있으므로 비동기 Job 방식으로 처리하며, 요청 직후 `job_id`를 반환합니다.

```http
POST /api/jobs
```

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|---|---|---:|---|
| `source_type` | `string` | O | `local`, `upload`, `velog`, `template` |
| `path` | `string` | X | 로컬 마크다운 폴더 경로 |
| `username` | `string` | X | Velog 사용자명 |
| `topic` | `string` | O | 작성할 글의 주제 |
| `doc_type` | `string` | O | 네 가지 문서 유형 중 하나 |
| `tone` | `string` | O | `경어체` 또는 `구어체` |
| `material` | `string` | X | 경험, 수치, 메모, 에러 메시지, 코드 조각 |

#### Example Request

```json
{
  "source_type": "local",
  "path": "./sample_posts",
  "topic": "파이썬 타입 힌트 도입기",
  "doc_type": "문제 해결 문서",
  "tone": "경어체",
  "material": "mypy 도입 첫 주에 에러 400개가 발생해 점진적 도입으로 전환한 경험"
}
```

#### Example Response

```json
{
  "job_id": "ecfbd9242d3b",
  "status": "running"
}
```

### 초안 작성 결과 조회

```http
GET /api/jobs/{job_id}
```

폴링 방식으로 작업 진행 상태와 완료 결과를 조회합니다.

```http
GET /api/jobs/{job_id}/stream
```

SSE 방식으로 `progress`, `result`, `error` 이벤트를 전달받습니다.

---

### 퇴고 요청

작성된 마크다운 글에서 오탈자와 논리 문제를 찾습니다.

사용자의 원문을 자동으로 재작성하지 않고, 문제의 위치와 수정 방향만 제공합니다.

```http
POST /api/reviews
```

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|---|---|---:|---|
| `draft` | `string` | O | 퇴고할 마크다운 원문 |
| `doc_type` | `string` | O | 네 가지 문서 유형 중 하나 |

#### Example Request

```json
{
  "draft": "# Redis 캐시 도입으로 조회 성능을 개선한 이야기\n\n...",
  "doc_type": "문제 해결 문서"
}
```

#### Example Response

```json
{
  "job_id": "7ab47fd283f1",
  "status": "running"
}
```

### 퇴고 결과 조회

```http
GET /api/reviews/{job_id}
```

```http
GET /api/reviews/{job_id}/stream
```

각 지적은 판정 방식에 따라 다음과 같이 구분됩니다.

| `source` | 설명 |
|---|---|
| `auto` | Python 코드 기반 결정적 검사 |
| `model` | 편집자 에이전트의 모델 판단 |

---

### 선택지 조회

프론트엔드에서 문서 유형과 말투 목록을 하드코딩하지 않도록 서버가 선택지를 제공합니다.

```http
GET /api/options
```

---

## External APIs

| 플랫폼 | 용도 | 비고 |
|---|---|---|
| OpenAI | 문체 분석, 초안 작성, 퇴고 | GPT-4o 계열 사용 |
| Velog | 사용자 글 목록 및 본문 조회 | 비공식 GraphQL API 사용 |

> Velog GraphQL API는 공식적으로 공개된 API가 아니므로 향후 변경될 수 있습니다.

---

## Project Structure

```text
server/
├── pipeline.py
│   └── run_pipeline(), run_review()
├── agents.py
│   └── Analyst, Writer, Editor Agent
├── tasks.py
│   └── 에이전트별 Task 정의
├── doc_types.py
│   └── 문서 유형 4종 템플릿
├── style_presets.py
│   └── 기존 글이 없는 사용자를 위한 기본 문체
├── checks.py
│   └── 코드 기반 결정적 검사
├── models.py
│   └── StyleGuide, EditReport 등 내부 자료구조
├── tokens.py
│   └── 단계별 토큰 사용량 계측
├── sources/
│   ├── local_md.py
│   └── velog.py
├── api.py
│   └── FastAPI 엔드포인트
├── jobs.py
│   └── 백그라운드 Job과 진행 이벤트 관리
└── cli.py
    └── CLI 진입점

client/
├── src/
│   ├── App.jsx
│   └── components/
│       ├── Landing
│       ├── FolderPicker
│       ├── StepShell
│       └── ChoiceList
└── package.json

sample_posts/
└── 데모용 마크다운 파일
```

---

## Contributors

| 이름 | 역할 |
|---|---|
| 박나원 | PM |
| 정유경 | Frontend |
| 최장우 | Backend |
