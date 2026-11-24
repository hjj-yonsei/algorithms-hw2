# 구현 계획서 (PLAN.md)

## 핵심 설계 원칙 (명세 준수 확인)
1. **내장 자료구조 금지**: `src/` 내 모든 모듈에서 `dict`, `set`, 내장 `hash()`를 사용하지 않고, 직접 구현한 `HashTable` 및 `LinearProbingHashTable`만 사용한다.
2. **단축 코드 생성 방식**: URL 해시값으로 코드를 만들면 충돌 위험이 있으므로, 순차 증가하는 정수 일련번호를 `base62.encode()`로 변환해 유일한 단축 코드를 생성한다.
3. **테스트 우선 개발(TDD)**: 구현 코드를 작성하기 전에 `SPEC.md` 6절의 경계 사례를 `unittest` 코드로 먼저 작성하고, 구현 후에는 테스트를 수정하지 않은 채 `make test`를 통과시킨다.

## 단계별 실행 계획
1. **1단계 — Base62 인코딩 (`src/base62.py`, `tests/test_base62.py`)**: `0-9a-zA-Z` 기반 `encode(n)` 및 `decode(s)` 구현 및 경계값 단위 테스트 통과.
2. **2단계 — 테스트 우선 작성 (`tests/test_hash_table.py`, `tests/test_shortener.py`)**: `SPEC.md` 6절의 경계 사례를 `unittest`로 먼저 작성.
3. **3단계 — 해시 테이블 구현 (`src/hash_table.py`, `src/linear_probing.py`)**: 호너 해시(`R=31`) 기반 개별 체이닝 `HashTable` 및 선형 탐지 `LinearProbingHashTable` 구현.
4. **4단계 — URL 단축기 구현 (`src/shortener.py`)**: URL 형식 검증 및 이중 해시 테이블 기반 단축기 구현 후 `make test` 통과 확인.
5. **5단계 — 규칙 검증 (`.github/copilot-instructions.md`)**: 금지 내장 기능(`dict`, `set(`, `hash(`) 정적 검사 및 규칙 파일 적용.
6. **6단계 — 적재율 및 충돌 해결 성능 실험 (`experiments/probe_experiment.py`, `experiments/compare_experiment.py`)**: $M=4093$ 고정 테이블 실험, CSV 및 순수 SVG 그래프 생성.
7. **7단계 — 웹 서버 구현 (`src/server.py`)**: 표준 `http.server` 기반 `/`, `/<code>`, `/table` 및 프록시 헤더(`X-Forwarded-Host`, `X-Forwarded-Proto`) 지원.