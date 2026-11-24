"""Linear-probing hash table with tombstone deletion."""

from src.hash_table import compute_horner


_EMPTY = object()
_DELETED = object()


class LinearProbingHashTable:
    def __init__(self, capacity=11, max_load=0.75):
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            raise ValueError("capacity는 양의 정수여야 합니다.")
        if max_load is not None:
            if not isinstance(max_load, (int, float)) or isinstance(max_load, bool):
                raise ValueError("max_load는 양의 실수 또는 None이어야 합니다.")
            if max_load <= 0:
                raise ValueError("max_load는 양의 실수 또는 None이어야 합니다.")
        self.capacity = capacity
        self.max_load = max_load
        self.slots = [_EMPTY] * capacity
        self.values = [None] * capacity
        self._size = 0
        self.last_probes = 0

    def __len__(self):
        return self._size

    def __contains__(self, key):
        _, found, _ = self.get_with_probes(key)
        return found

    def _resize_if_needed(self):
        if self.max_load is None:
            return
        if self._size / self.capacity <= self.max_load:
            return

        old_slots = self.slots
        old_values = self.values
        new_capacity = self.capacity * 2
        while not self._is_prime(new_capacity):
            new_capacity += 1
        self.capacity = new_capacity
        self.slots = [_EMPTY] * new_capacity
        self.values = [None] * new_capacity
        self._size = 0
        for i in range(len(old_slots)):
            if old_slots[i] is not _EMPTY and old_slots[i] is not _DELETED:
                self.put(old_slots[i], old_values[i])

    @staticmethod
    def _is_prime(n):
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        divisor = 3
        while divisor * divisor <= n:
            if n % divisor == 0:
                return False
            divisor += 2
        return True

    def put(self, key, value):
        if self._size >= self.capacity and self.max_load is None:
            raise OverflowError("해시 테이블이 가득 찼습니다.")

        start = compute_horner(key, self.capacity)
        first_deleted = -1
        for step in range(self.capacity):
            index = (start + step) % self.capacity
            slot = self.slots[index]
            if slot is _EMPTY:
                if first_deleted >= 0:
                    index = first_deleted
                self.slots[index] = key
                self.values[index] = value
                self._size += 1
                self._resize_if_needed()
                return
            if slot is _DELETED:
                if first_deleted < 0:
                    first_deleted = index
            elif slot == key:
                self.values[index] = value
                return
        raise OverflowError("해시 테이블이 가득 찼습니다.")

    def get_with_probes(self, key):
        start = compute_horner(key, self.capacity)
        for step in range(self.capacity):
            index = (start + step) % self.capacity
            slot = self.slots[index]
            if slot is _EMPTY:
                probes = step + 1
                self.last_probes = probes
                return None, False, probes
            if slot is not _DELETED and slot == key:
                probes = step + 1
                self.last_probes = probes
                return self.values[index], True, probes
        self.last_probes = self.capacity
        return None, False, self.capacity

    def get(self, key):
        value, found, probes = self.get_with_probes(key)
        self.last_probes = probes
        return value if found else None

    def delete(self, key):
        start = compute_horner(key, self.capacity)
        for step in range(self.capacity):
            index = (start + step) % self.capacity
            slot = self.slots[index]
            if slot is _EMPTY:
                return False
            if slot is not _DELETED and slot == key:
                self.slots[index] = _DELETED
                self.values[index] = None
                self._size -= 1
                return True
        return False
