# URL 단축기 명세서 (SPEC.md)

## 1. 개요
본 시스템은 긴 URL을 짧은 Base62 코드로 변환하고, 짧은 코드로 원래 URL을 조회·리다이렉트하는 웹 서비스이다. Python 표준 라이브러리만 사용하며, 핵심 자료구조인 해시 테이블은 외부 라이브러리나 파이썬 내장 `dict`, `set`, `hash()` 없이 직접 구현한다.

## 2. Base62 인코딩 (`src/base62.py`)
- 문자 집합(62자): `0-9` (0~9), `a-z` (10~35), `A-Z` (36~61) 순서의 문자열 `"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"`를 사용한다.
- `encode(n: int) -> str`: 0 이상의 정수를 62진법 문자열로 변환한다. `encode(0)`은 `"0"`을 반환한다. 음수나 정수가 아닌 입력(`bool` 포함)은 예외(`ValueError` 또는 `TypeError`)를 발생시킨다.
- `decode(s: str) -> int`: Base62 문자열을 10진 정수로 복원한다. 빈 문자열이나 허용되지 않은 문자가 포함되면 `ValueError`를 발생시킨다.

## 3. 해시 함수 및 해시 테이블 (`src/hash_table.py`, `src/linear_probing.py`)
- **호너(Horner) 해시 함수**:
  - 기수 $R = 31$, 테이블 크기 $M$에 대해 초기값 $h = 0$에서 시작하여 문자열의 각 문자 $c$마다 $h \leftarrow (31 \cdot h + \text{ord}(c)) \bmod M$을 계산한다.
  - `horner_steps(key, capacity)`는 각 글자별 `(문자, 아스키/유니코드 코드, 이전 h, 계산된 h)` 과정을 반환해 웹 시각화(`/table`)에 활용한다.
- **개별 체이닝 (`HashTable`)**:
  - 각 버킷은 연결 리스트(`_ChainNode`)의 헤드를 저장한다.
  - 생성자: `HashTable(capacity=11, max_load=0.75)`. `max_load`가 `None`이면 크기를 고정하고 리해싱하지 않는다.
  - 적재율 $\alpha = N / M$이 `max_load`를 초과하면 현재 크기의 2배 이상인 가장 작은 소수로 버킷 배열을 확장하고 모든 원소를 재삽입한다.
  - 탐색 시 비교한 노드 수(`last_probes`)를 기록한다. 버킷이 비어 있으면 비교 노드 수는 `0`이다.
- **선형 탐지 (`LinearProbingHashTable`)**:
  - `HashTable`과 동일한 메서드 인터페이스(`put`, `get`, `delete`, `__contains__`, `__len__`, `get_with_probes`)를 제공한다.
  - 충돌 발생 시 `(h + step) % M` 순서로 다음 빈 칸을 탐지하며, 테이블 끝(`M - 1`)에 도달하면 `0`번 칸으로 순환(wrap-around)한다.
  - 삭제 시 삭제 표시(Tombstone)를 사용해 이후 키의 탐지 경로가 끊기지 않도록 유지한다.
  - `max_load=None`인 상태에서 테이블이 가득 찬 경우 새 키 삽입 시 `OverflowError`를 발생시키며, 가득 찬 테이블에서 없는 키를 탐색할 때 무한 루프 없이 최대 $M$칸만 확인 후 종료한다.
  - 탐색 시 들여다본 칸 수(`last_probes`)를 기록한다.

## 4. URL 단축기 (`src/shortener.py`)
- `URLShortener(table_type="chaining", capacity=11, max_load=0.75)`는 `"chaining"`(`HashTable`) 또는 `"linear"`(`LinearProbingHashTable`) 중 하나를 선택해 `url_to_code`와 `code_to_url` 두 테이블을 관리한다.
- **단축 코드 발급**: 해시값이 아니라 1부터 1씩 증가하는 순차 일련번호를 `base62.encode()`로 변환해 충돌 없는 고유 코드를 발급한다.
- **중복 URL 처리**: 이미 등록된 동일한 URL을 다시 요청하면 새 코드를 발급하지 않고 기존 단축 코드를 그대로 반환한다.
- **입력 검증**: `http://` 또는 `https://`로 시작하는 유효한 호스트를 가진 문자열만 허용한다. `ftp://` 등 다른 스킴, 빈 문자열, 공백 포함 문자열, 호스트 누락(`http://`), 2048자 초과 URL은 `ValueError`를 발생시킨다.
- **조회 (`resolve(code)`)**: 등록된 단축 코드면 원본 URL을 반환하고, 존재하지 않거나 유효하지 않은 코드면 `None`을 반환한다.

## 5. 웹 서비스 (`src/server.py`)
- Python 표준 라이브러리 `http.server`만 사용하며 포트 `8000`에서 실행한다.
- `GET /`: URL 입력 폼과 단축 결과 화면을 제공한다.
- `POST /shorten` (및 `POST /`): 폼 데이터 또는 JSON의 `url`을 단축해 짧은 링크를 보여 준다. 링크 생성 시 `X-Forwarded-Proto`와 `X-Forwarded-Host` 헤더를 `Host` 헤더보다 우선 확인한다.
- `GET /<code>`: 등록된 코드면 원본 URL로 `302 Found` 리다이렉트하고, 없으면 `404 Not Found`를 응답한다.
- `GET /table`: 현재 해시 테이블의 버킷 상태를 시각화한다. 개별 체이닝은 연결 리스트 노드와 `NULL` 끝을 화살표로 표시하고, 선형 탐지는 슬롯 점유 상태와 탐지 거리를 표시하며, 각 항목을 펼치면 글자별 호너 해시 계산 과정을 보여 준다.

## 6. 경계 사례 (Edge Cases)
1. **Base62 경계값**: `encode(0) == "0"`, `decode("0") == 0`, `encode(61) == "Z"`, `encode(62) == "10"`, `encode(3843) == "ZZ"`, `encode(3844) == "100"`, `encode(100000000) == "6LAze"`, 음수·불리언·빈 문자열·특수문자 입력 시 예외 발생.
2. **호너 해시 및 해시 테이블 경계값**: 빈 문자열 키 `""`의 호너 해시는 `0`, 아나그램(`"stop"`, `"pots"`, `"tops"`, `"spot"`, `"opts"`, `"post"`) 분산, 동일 키 재삽입 시 크기 유지 및 값 갱신, 없는 키 조회/삭제, 적재율 초과 시 리해싱 후 데이터 보존, `max_load=None` 고정 크기 동작.
3. **선형 탐지 전용 경계값**: 끝 칸(`M - 1`) 충돌 시 `0`번 칸으로 순환(wrap-around), 중간 삭제 후 뒤쪽 원소 조회 유지(Tombstone), 가득 찬 테이블 삽입 시 `OverflowError`, 가득 찬 테이블에서 없는 키 조회 시 무한 루프 없이 `None` 반환.
4. **URL 단축기 경계값**: 동일 URL 중복 요청 시 기존 코드 반환, 잘못된 스킴(`ftp://`, `javascript:`), 빈 문자열/공백 포함, 호스트 누락(`https://`), 2048자 초과 입력 시 `ValueError`, 없는 코드 조회 시 `None`, 체이닝과 선형 탐지 양쪽 모두 동일 동작.
