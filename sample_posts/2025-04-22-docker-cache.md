---
title: "도커 빌드가 매번 8분 걸리던 걸 40초로"
date: 2025-04-22
tags: [docker, ci]
---

CI에서 이미지 빌드에 8분씩 걸렸습니다. 코드 한 줄만 고쳐도 8분이었죠.

## 무엇이 캐시를 깨고 있었나

도커는 레이어 단위로 캐시합니다. 앞 레이어가 바뀌면 뒤 레이어는 전부 다시 만듭니다. 그래서 자주 바뀌는 것을 뒤로 보내는 게 기본입니다.

문제의 Dockerfile은 이렇게 시작하고 있었습니다.

```dockerfile
COPY . /app
RUN pip install -r requirements.txt
```

소스를 통째로 먼저 복사하니, 코드 한 글자만 바뀌어도 `COPY` 레이어가 무효화됩니다. 그 뒤의 `pip install` 도 당연히 다시 돕니다. 의존성은 그대로인데 매번 새로 받는 셈이죠.

## 순서를 바꿨습니다

```dockerfile
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
```

의존성 목록만 먼저 복사하고 설치한 뒤에 소스를 복사합니다. `requirements.txt` 가 안 바뀌면 설치 레이어는 캐시에서 그대로 나옵니다.

이것만으로 8분이 1분 20초가 됐습니다.

## 한 걸음 더

CI 러너는 매번 새 머신이라 로컬 캐시가 없습니다. 레지스트리에 있는 이전 이미지를 캐시 소스로 지정했습니다.

```bash
docker build \
  --cache-from myrepo/app:latest \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t myrepo/app:latest .
```

여기까지 하니 40초입니다.

## 정리

- 자주 바뀌는 파일은 Dockerfile 뒤쪽에 둔다
- 의존성 설치와 소스 복사를 분리한다
- CI에서는 `--cache-from` 으로 이전 이미지를 끌어다 쓴다

빌드 시간은 하루에 몇 번씩 지불하는 비용입니다. 한 번 줄여 두면 계속 돌려받습니다.
