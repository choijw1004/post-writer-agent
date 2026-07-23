"""전역 설정. 값의 근거는 docs/docs.md 의 '수업 개념 ↔ 설계 연결' 표를 따른다."""

import os

from dotenv import load_dotenv

load_dotenv()

# 개발 중엔 gpt-4o-mini, 최종 데모만 상위 모델로 올린다.
MODEL = os.getenv("BLOG_AGENT_MODEL", "gpt-4o-mini")

# gpt-4o / gpt-4o-mini 계열의 토크나이저.
ENCODING_NAME = os.getenv("BLOG_AGENT_ENCODING", "o200k_base")

# ── 컨텍스트 윈도우 대응 ────────────────────────────────────────────────
# 문체 샘플을 통째로 넣지 않는 이유: 프롬프트에 넣는 토큰은 곧 비용이자
# Self-Attention 의 N^2 연산 대상이다. 그래서 샘플은 '토큰 예산' 안에서만
# 싣고, 예산을 넘기면 글 단위로 잘라낸다. (docs.md 컨텍스트 윈도우 항목)
STYLE_SAMPLE_TOKEN_BUDGET = int(os.getenv("STYLE_SAMPLE_TOKEN_BUDGET", "6000"))

# 글 하나에서 발췌할 최대 토큰. 문체는 앞부분만 봐도 대체로 드러난다.
PER_POST_TOKEN_CAP = int(os.getenv("PER_POST_TOKEN_CAP", "1200"))

# 예산이 남아도 이 개수를 넘기지 않는다(지시 희석 방지).
MAX_STYLE_SAMPLES = int(os.getenv("MAX_STYLE_SAMPLES", "5"))

LENGTH_SPEC = {
    "짧게": "800~1200자, 소제목 2~3개",
    "보통": "1500~2500자, 소제목 3~5개",
    "길게": "3000~4500자, 소제목 5개 이상",
}

# ── velog (비공식 API) ─────────────────────────────────────────────────
VELOG_API_URL = os.getenv("VELOG_API_URL", "https://v3.velog.io/graphql")
VELOG_TIMEOUT = float(os.getenv("VELOG_TIMEOUT", "15"))

# 목록과 본문이 별도 쿼리라 글 수만큼 요청이 나간다. 어차피 뒤에서 토큰
# 예산으로 더 줄어들기 때문에 애초에 최근 몇 편만 가져온다.
VELOG_FETCH_LIMIT = int(os.getenv("VELOG_FETCH_LIMIT", "8"))

# 사용자 입력 선택지. CLI 와 API 가 같은 목록을 공유한다.
AUDIENCES = ["주니어 개발자", "동료 개발자", "비개발자", "일반 독자"]
PURPOSES = ["학습 정리", "트러블슈팅 공유", "회고", "튜토리얼"]
LENGTHS = list(LENGTH_SPEC)

# React 개발 서버 오리진. 배포 시 환경변수로 덮어쓴다.
CORS_ORIGINS = os.getenv(
    "BLOG_AGENT_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
).split(",")
