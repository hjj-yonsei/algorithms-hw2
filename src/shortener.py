"""URL shortening service backed by the project's hash tables."""

from urllib.parse import urlsplit

from src.base62 import decode, encode
from src.hash_table import HashTable
from src.linear_probing import LinearProbingHashTable


class URLShortener:
    def __init__(self, table_type="chaining", capacity=11, max_load=0.75):
        if table_type not in ("chaining", "linear"):
            raise ValueError("table_type은 chaining 또는 linear이어야 합니다.")

        if table_type == "chaining":
            self.url_to_code = HashTable(capacity=capacity, max_load=max_load)
            self.code_to_url = HashTable(capacity=capacity, max_load=max_load)
        else:
            self.url_to_code = LinearProbingHashTable(
                capacity=capacity, max_load=max_load
            )
            self.code_to_url = LinearProbingHashTable(
                capacity=capacity, max_load=max_load
            )
        self._next_number = 1
        self.table_type = table_type

    def _validate_url(self, url):
        if not isinstance(url, str):
            raise ValueError("유효한 URL 문자열이어야 합니다.")
        if not url or len(url) > 2048 or any(ch.isspace() for ch in url):
            raise ValueError("유효한 URL 문자열이어야 합니다.")

        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL은 http 또는 https로 시작해야 합니다.")
        if not parsed.netloc or parsed.hostname is None:
            raise ValueError("URL에는 유효한 호스트가 필요합니다.")
        return url

    def shorten(self, url):
        url = self._validate_url(url)

        existing = self.url_to_code.get(url)
        if existing is not None:
            return existing

        code = encode(self._next_number)
        self._next_number += 1
        self.url_to_code.put(url, code)
        self.code_to_url.put(code, url)
        return code

    def resolve(self, code):
        if not isinstance(code, str) or not code:
            return None
        if any(ch not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in code):
            return None
        try:
            decode(code)
        except (TypeError, ValueError):
            return None
        return self.code_to_url.get(code)

    def __len__(self):
        return len(self.url_to_code)
