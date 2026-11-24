"""선형 탐지(Linear Probing) 기반 해시 테이블 직접 구현."""

from src.hash_table import compute_horner


_EMPTY = 0
_OCCUPIED = 1
_DELETED = 2


def _next_prime(value: int) -> int:
    candidate = max(value, 2)
    while True:
        is_prime = candidate >= 2
        for divisor in range(2, int(candidate ** 0.5) + 1):
            if candidate % divisor == 0:
                is_prime = False
                break
        if is_prime:
            return candidate
        candidate += 1


class LinearProbingHashTable:
    """개방 주소법의 선형 탐지와 호너 해시를 사용하는 해시 테이블."""

    def __init__(self, capacity: int = 11, max_load: float | None = 0.75):
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
            raise ValueError("초기 용량은 1 이상의 정수여야 합니다.")
        if max_load is not None and (max_load <= 0 or max_load >= 1):
            raise ValueError("선형 탐지의 최대 적재율은 0보다 크고 1보다 작아야 합니다.")

        self.capacity = capacity
        self.max_load = max_load
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.states = [_EMPTY] * self.capacity
        self.size = 0
        self.last_probes = 0

    def __len__(self) -> int:
        return self.size

    def load_factor(self) -> float:
        return self.size / self.capacity

    def _resize(self, new_capacity: int) -> None:
        old_keys = self.keys
        old_values = self.values
        old_states = self.states

        self.capacity = new_capacity
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.states = [_EMPTY] * self.capacity
        self.size = 0

        for i in range(len(old_keys)):
            if old_states[i] == _OCCUPIED:
                self._insert_without_resize(old_keys[i], old_values[i])

    def _insert_without_resize(self, key: str, value: object) -> int:
        start_idx = compute_horner(key, self.capacity)
        first_deleted = -1

        for step in range(self.capacity):
            idx = (start_idx + step) % self.capacity
            state = self.states[idx]

            if state == _EMPTY:
                target = first_deleted if first_deleted != -1 else idx
                self.keys[target] = key
                self.values[target] = value
                self.states[target] = _OCCUPIED
                self.size += 1
                return step + 1

            if state == _DELETED:
                if first_deleted == -1:
                    first_deleted = idx
            elif self.keys[idx] == key:
                self.values[idx] = value
                return step + 1

        if first_deleted != -1:
            self.keys[first_deleted] = key
            self.values[first_deleted] = value
            self.states[first_deleted] = _OCCUPIED
            self.size += 1
            return self.capacity

        raise OverflowError("선형 탐지 해시 테이블이 가득 찼습니다.")

    def put(self, key: str, value: object) -> None:
        if not isinstance(key, str):
            raise TypeError("키는 문자열이어야 합니다.")

        if self.max_load is not None:
            _, found, _ = self.get_with_probes(key)
            if not found and ((self.size + 1) / self.capacity) > self.max_load:
                self._resize(_next_prime(self.capacity * 2))

        self.last_probes = self._insert_without_resize(key, value)

    def get_with_probes(self, key: str) -> tuple:
        if not isinstance(key, str):
            raise TypeError("키는 문자열이어야 합니다.")

        start_idx = compute_horner(key, self.capacity)
        for step in range(self.capacity):
            idx = (start_idx + step) % self.capacity
            probed = step + 1
            state = self.states[idx]

            if state == _EMPTY:
                self.last_probes = probed
                return None, False, probed

            if state == _OCCUPIED and self.keys[idx] == key:
                self.last_probes = probed
                return self.values[idx], True, probed

        self.last_probes = self.capacity
        return None, False, self.capacity

    def get(self, key: str, default: object = None) -> object:
        value, found, _ = self.get_with_probes(key)
        return value if found else default

    def __contains__(self, key: str) -> bool:
        _, found, _ = self.get_with_probes(key)
        return found

    def delete(self, key: str) -> bool:
        if not isinstance(key, str):
            raise TypeError("키는 문자열이어야 합니다.")

        start_idx = compute_horner(key, self.capacity)
        for step in range(self.capacity):
            idx = (start_idx + step) % self.capacity
            probed = step + 1
            state = self.states[idx]

            if state == _EMPTY:
                self.last_probes = probed
                return False

            if state == _OCCUPIED and self.keys[idx] == key:
                self.keys[idx] = None
                self.values[idx] = None
                self.states[idx] = _DELETED
                self.size -= 1
                self.last_probes = probed
                return True

        self.last_probes = self.capacity
        return False

    def items(self) -> list:
        return [
            (self.keys[i], self.values[i])
            for i in range(self.capacity)
            if self.states[i] == _OCCUPIED
        ]
