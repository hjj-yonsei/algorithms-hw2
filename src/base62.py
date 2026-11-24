"""0-9, a-z, A-Z 순서의 Base62 인코딩 및 디코딩 모듈."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = 62


def _char_to_val(ch: str) -> int:
    code = ord(ch)
    if 48 <= code <= 57:
        return code - 48
    if 97 <= code <= 122:
        return code - 97 + 10
    if 65 <= code <= 90:
        return code - 65 + 36
    raise ValueError(f"유효하지 않은 Base62 문자입니다: {ch!r}")


def encode(n: int) -> str:
    """0 이상의 정수를 Base62 문자열로 변환한다."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("정수만 인코딩할 수 있습니다.")
    if n < 0:
        raise ValueError("0 이상의 정수만 인코딩할 수 있습니다.")
    if n == 0:
        return "0"

    chars = []
    num = n
    while num > 0:
        num, rem = divmod(num, BASE)
        chars.append(ALPHABET[rem])
    chars.reverse()
    return "".join(chars)


def decode(s: str) -> int:
    """Base62 문자열을 0 이상의 정수로 복원한다."""
    if not isinstance(s, str):
        raise TypeError("문자열만 디코딩할 수 있습니다.")
    if len(s) == 0:
        raise ValueError("빈 문자열은 디코딩할 수 없습니다.")

    result = 0
    for ch in s:
        result = result * BASE + _char_to_val(ch)
    return result
