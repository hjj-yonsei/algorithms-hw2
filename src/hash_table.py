"""Separate-chaining hash table with a Horner hash."""


class _ChainNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


def compute_horner(key: str, capacity: int) -> int:
    if not isinstance(key, str):
        raise TypeError("키는 문자열이어야 합니다.")
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
        raise ValueError("capacity는 양의 정수여야 합니다.")

    h = 0
    for ch in key:
        h = (31 * h + ord(ch)) % capacity
    return h


def horner_steps(key: str, capacity: int):
    steps = []
    h = 0
    for ch in key:
        previous = h
        h = (31 * h + ord(ch)) % capacity
        steps.append((ch, ord(ch), previous, h))
    return steps


def _is_prime(n: int) -> bool:
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


def _next_prime(n: int) -> int:
    candidate = max(2, n)
    if candidate % 2 == 0:
        candidate += 1
    while not _is_prime(candidate):
        candidate += 2
    return candidate


class HashTable:
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
        self.buckets = [None] * capacity
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
        new_capacity = _next_prime(self.capacity * 2)
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [None] * new_capacity
        self._size = 0

        for head in old_buckets:
            node = head
            while node is not None:
                self.put(node.key, node.value)
                node = node.next

    def put(self, key, value):
        index = compute_horner(key, self.capacity)
        head = self.buckets[index]
        node = head
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next

        new_node = _ChainNode(key, value)
        new_node.next = head
        self.buckets[index] = new_node
        self._size += 1
        self._resize_if_needed()

    def get_with_probes(self, key):
        index = compute_horner(key, self.capacity)
        node = self.buckets[index]
        probes = 0
        while node is not None:
            probes += 1
            if node.key == key:
                self.last_probes = probes
                return node.value, True, probes
            node = node.next
        self.last_probes = 0
        return None, False, 0

    def get(self, key):
        value, found, probes = self.get_with_probes(key)
        self.last_probes = probes
        return value if found else None

    def delete(self, key):
        index = compute_horner(key, self.capacity)
        previous = None
        node = self.buckets[index]
        while node is not None:
            if node.key == key:
                if previous is None:
                    self.buckets[index] = node.next
                else:
                    previous.next = node.next
                self._size -= 1
                return True
            previous = node
            node = node.next
        return False
