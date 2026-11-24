ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode(n):
    """Encode a non-negative integer as a base62 string."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return "0"

    result = []
    while n:
        n, remainder = divmod(n, BASE)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))


def decode(s):
    """Decode a base62 string into an integer."""
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    if not s:
        raise ValueError("s must not be empty")

    value = 0
    for char in s:
        index = ALPHABET.find(char)
        if index == -1:
            raise ValueError("invalid base62 character: " + char)
        value = value * BASE + index
    return value
