# CS Study Dashboard

CS 면접 대비 학습 대시보드. 9개 챕터 × 110개 = 총 990개 주제의 질문과 해설을 담고 있습니다.

## 웹으로 보기

👉 https://seungmin123.github.io/cs-study/

## 로컬에서 보기

정적 사이트라 별도 빌드가 없습니다. `index.html`을 로컬 HTTP 서버로 열면 됩니다:

```bash
python3 -m http.server 8000
# → http://127.0.0.1:8000/index.html
```

> `file://`로 직접 열면 브라우저가 큰 로컬 스크립트(`topics.js`) 로딩을 차단할 수 있으므로 HTTP 서버 사용을 권장합니다.

## 구성

- `index.html` — 대시보드 (챕터·난이도·검색 필터, 진도 표시, 해설 모달)
- `topics.js` / `topics.json` — 전체 주제 데이터 (항상 동기화)
- `notes/01~09_*.md` — 챕터별 학습 노트

## 챕터

자료구조 & 알고리즘 · 운영체제 · 네트워크 · 데이터베이스 · 컴퓨터 구조 · 소프트웨어 설계 · 시스템 디자인 · Java · Spring
