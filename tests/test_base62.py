import unittest
from src.base62 import decode, encode


class TestBase62(unittest.TestCase):
    def test_zero_and_single_digits(self):
        self.assertEqual(encode(0), "0")
        self.assertEqual(decode("0"), 0)
        self.assertEqual(encode(9), "9")
        self.assertEqual(encode(10), "a")
        self.assertEqual(encode(35), "z")
        self.assertEqual(encode(36), "A")
        self.assertEqual(encode(61), "Z")
        self.assertEqual(decode("Z"), 61)

    def test_multi_digit_boundaries(self):
        self.assertEqual(encode(62), "10")
        self.assertEqual(decode("10"), 62)
        self.assertEqual(encode(3843), "ZZ")
        self.assertEqual(encode(3844), "100")
        self.assertEqual(decode("100"), 3844)
        self.assertEqual(encode(100_000_000), "6LAze")
        self.assertEqual(decode("6LAze"), 100_000_000)

    def test_roundtrip(self):
        for value in [0, 1, 61, 62, 12345, 999999999]:
            self.assertEqual(decode(encode(value)), value)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            encode(-1)
        with self.assertRaises(TypeError):
            encode(True)
        with self.assertRaises(TypeError):
            encode("10")
        with self.assertRaises(ValueError):
            decode("")
        with self.assertRaises(ValueError):
            decode("abc-123")
        with self.assertRaises(TypeError):
            decode(123)


if __name__ == "__main__":
    unittest.main()
