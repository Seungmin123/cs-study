#!/usr/bin/env python3
"""
모든 answers_*.json 파일의 answer/level/covered 정보를 topics.js에 병합합니다.
"""
import json
import glob
import re
import sys
from datetime import date

TOPICS_JS = "topics.js"
TODAY = date.today().isoformat()  # "2026-06-15"

# ── 1. 모든 answer 파일 로드 ──────────────────────────────────────────────────
print("▶ answer 파일 로드 중...")
patch_map = {}  # id → {answer, level, ...}

for filepath in sorted(glob.glob("answers_*.json")):
    with open(filepath) as f:
        data = json.load(f)

    items = []
    if isinstance(data, list):
        # 새 형식: [{id, level, answer, ...}, ...]
        items = data
    elif isinstance(data, dict):
        # 구 형식: {id: "answer 텍스트"} 또는 {id: {answer, level, ...}}
        for tid, val in data.items():
            if isinstance(val, str):
                items.append({"id": tid, "answer": val})
            elif isinstance(val, dict):
                val["id"] = tid
                items.append(val)

    count = 0
    for item in items:
        tid = item.get("id")
        if not tid:
            continue
        if tid in patch_map:
            # answer 없으면 무시, 있으면 덮어쓰기 (최신 우선)
            pass
        else:
            patch_map[tid] = item
            count += 1
    print(f"  • {filepath}: {count}개")

print(f"  총 {len(patch_map)}개 ID 로드됨\n")

# ── 2. topics.js 읽기 ─────────────────────────────────────────────────────────
print("▶ topics.js 읽기...")
with open(TOPICS_JS, encoding="utf-8") as f:
    js_content = f.read()

# var TOPICS = {...}; 에서 JSON 부분 추출
m = re.match(r'^\s*var\s+TOPICS\s*=\s*([\s\S]+?);\s*$', js_content.strip())
if not m:
    print("ERROR: topics.js 파싱 실패. 'var TOPICS = {...};' 형식인지 확인하세요.")
    sys.exit(1)

topics_json = json.loads(m.group(1))
print("  파싱 성공\n")

# ── 3. 병합 ───────────────────────────────────────────────────────────────────
print("▶ 병합 중...")
updated = 0
not_found_in_topics = []
not_found_in_patch = []

chapters = topics_json.get("chapters", {})
all_topic_ids = set()

for chapter_key, chapter in chapters.items():
    for topic in chapter.get("topics", []):
        tid = topic["id"]
        all_topic_ids.add(tid)

        # 항상 covered/coveredAt 초기화 (사전 채움이므로 학습 진행 아님)
        topic["covered"] = False
        topic["coveredAt"] = None

        if tid in patch_map:
            patch = patch_map[tid]
            # answer 필드 업데이트
            if patch.get("answer"):
                topic["answer"] = patch["answer"]
            # level 업데이트 (patch에 있으면)
            if patch.get("level"):
                topic["level"] = patch["level"]
            updated += 1
        else:
            not_found_in_patch.append(tid)

for tid in patch_map:
    if tid not in all_topic_ids:
        not_found_in_topics.append(tid)

print(f"  업데이트된 topic: {updated}개")
if not_found_in_patch:
    print(f"  ⚠ patch 없는 topic ({len(not_found_in_patch)}개): {not_found_in_patch[:10]}")
if not_found_in_topics:
    print(f"  ⚠ topics.js에 없는 patch ID ({len(not_found_in_topics)}개): {not_found_in_topics}")
print()

# ── 4. topics.js 저장 ─────────────────────────────────────────────────────────
print("▶ topics.js 저장 중...")
new_json = json.dumps(topics_json, ensure_ascii=False, indent=2)
new_js = f"var TOPICS = {new_json};\n"

# 백업
with open(TOPICS_JS + ".bak", "w", encoding="utf-8") as f:
    f.write(js_content)
print("  백업: topics.js.bak")

with open(TOPICS_JS, "w", encoding="utf-8") as f:
    f.write(new_js)
print(f"  저장 완료: {TOPICS_JS}")

# ── 5. topics.json도 동기화 ───────────────────────────────────────────────────
print("▶ topics.json 저장 중...")
with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(topics_json, f, ensure_ascii=False, indent=2)
print("  저장 완료: topics.json\n")

# ── 6. 요약 ───────────────────────────────────────────────────────────────────
total = len(all_topic_ids)
print("=" * 50)
print(f"✅ 병합 완료!")
print(f"   전체 topic: {total}개")
print(f"   answer 채워진 topic: {updated}개 ({updated/total*100:.1f}%)")
print(f"   미완성 topic: {total - updated}개")
