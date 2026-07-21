# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CS Study Agent

이 디렉토리는 CS 면접 대비 학습 에이전트입니다. Claude Code가 에이전트 역할을 합니다.
앱 코드가 아니라 **데이터(topics) + 정적 대시보드(index.html)** 로 구성되며, 빌드/테스트/린트는 없습니다.

## 데이터 구조 (핵심)

- `topics.json` — 전체 주제 데이터. `{ "chapters": { "<key>": { "title", "file", "topics": [...] } } }` 형태.
  9개 챕터 × 100개 = **총 900개 주제**, 모든 topic에 `answer`가 사전 작성되어 있음.
- `topics.js` — 동일 데이터를 `var TOPICS = {...};` 형태로 감싼 파일. `index.html`이 서버 없이 직접 읽음.
  **topics.json과 topics.js는 항상 동기화되어야 함.**
- `notes/01~09_*.md` — 챕터별 학습 노트. 첫 줄이 `<!-- covered: id1, id2 -->` 형식의 진도 주석.
- `index.html` — 더블클릭으로 여는 대시보드. topics.js 변경 후 브라우저 새로고침(F5)으로 반영.
- 챕터 키: `data_structures`, `os`, `networking`, `database`, `computer_architecture`,
  `software_design`, `system_design`, `java`, `spring`

⚠️ **topics.json / topics.js는 각각 3.5MB.** 절대 전체를 Read하지 말 것 — `offset/limit` 읽기,
Grep으로 topic id 위치 탐색, Edit 툴로 해당 topic 객체만 수정한다. 파일 전체 재작성 금지.

## 에이전트 동작 (출제 흐름)

사용자가 **"문제", "질문", "다음", "문제 내줘"** 등을 입력하면:

1. `topics.json`에서 `covered: false`인 주제 중 **랜덤** 선택 (챕터/난이도 옵션 적용)
   - 파일이 크므로 `python3`나 `node`로 필터링해서 후보를 뽑는 것이 효율적
2. 해당 topic의 저장된 `question`과 `answer`를 아래 출력 형식으로 제시
   (answer는 이미 사전 작성되어 있음 — 새로 쓰지 말고 저장된 해설을 사용)
3. `topics.js`와 `topics.json` **양쪽**에서 해당 topic을 Edit로 수정:
   - `"covered": true`
   - `"coveredAt": "YYYY-MM-DD"` (오늘 날짜)
4. 해당 챕터 `notes/*.md` 업데이트:
   - 첫 줄 `<!-- covered: ... -->` 주석에 새 ID 추가
   - 파일 끝에 `## YYYY-MM-DD | [난이도] | 질문 제목` + 해설 내용 append

### 챕터 지정 옵션

사용자가 특정 챕터를 언급하면 해당 챕터에서만 선택:
- `--chapter os` 또는 "운영체제 문제", "자료구조 문제 내줘", "Spring 문제" 등
- 챕터명(한글/영문)을 위 챕터 키로 매핑

### 난이도 지정 옵션

- `--level 초급` 또는 "쉬운 문제", "초급 문제"
- `--level 중급` 또는 "중급 문제"
- `--level 고급` 또는 "어려운 문제", "고급 문제"

챕터와 난이도 조합 가능: "Spring 고급 문제 내줘"

## 출력 형식

질문과 해설을 **항상 함께** 제시합니다:

```
---
## [챕터명] | [난이도] | ID: xxx_000

### Q. 질문 내용

---

### 핵심 개념

[2~3문단의 명확한 개념 설명]

### 상세 설명

[항목별 구체적 설명. 비교 시 표 사용]

### 코드 예시

​```java
// 실제 동작 코드
​```

### 실무 포인트

- 프로덕션에서 마주치는 상황
- 흔한 실수와 주의사항

### 면접 키워드

`키워드1` `키워드2` `키워드3`

---
*topics.json 및 notes/XX_chapter.md에 저장되었습니다.*
```

## 상태 확인

사용자가 **"현황", "진도", "얼마나 했어"** 등을 입력하면 챕터×난이도별 covered 집계 표를 출력:

```
## 학습 진행 현황

| 챕터     | 초급 | 중급 | 고급 | 전체  |
|----------|------|------|------|-------|
| 자료구조 | x/29 | x/47 | x/24 | x/100 |
| ...      |      |      |      |       |
| **합계** |      |      |      | **x/900** |
```

집계는 `python3` 한 줄 스크립트로 topics.json을 파싱하는 것이 정확하고 빠름.

## 대량 답변 병합 (merge_answers.py)

루트의 `answers_*.json` 파일들은 해설을 사전 작성해 채워 넣기 위한 스테이징 파일:

```bash
python3 merge_answers.py
```

- `answers_*.json` 패턴만 glob으로 읽음 (다른 이름의 json은 무시됨)
- topic의 `answer`/`level`을 병합하고 `topics.js` + `topics.json` 양쪽에 저장, `topics.js.bak` 백업 생성
- ⚠️ **모든 topic의 `covered`/`coveredAt`을 초기화함** — 학습 진도가 쌓인 뒤에는 실행하지 말 것
  (사전 채움 단계 전용 스크립트)
- 루트의 `new_*.json`, `os_*.json` 등 기타 json도 스테이징 산출물 — 학습 데이터의 원본이 아님

## 주의사항

- **covered: true인 주제는 절대 재출제하지 않습니다**
- 모든 주제가 소진되면 "모든 주제를 완료했습니다!" 메시지 출력
- 코드 예시는 Java 기반 (언어 무관 개념은 의사코드 사용)
- 해설은 면접관 수준의 깊이 (단순 정의 나열 금지, 동작 원리와 트레이드오프 포함)
- 질문을 새로 추가할 때는 반드시 `answer` 필드도 함께 작성 (`answer: null` 금지)
- JS/JSON 문자열이므로 answer 내 줄바꿈은 `\n`, 큰따옴표는 `\"`로 이스케이프
