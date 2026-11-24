import unittest

from src.base62 import decode, encode


class Base62Test(unittest.TestCase):
    def test_encode_zero(self):
        self.assertEqual(encode(0), "0")

    def test_encode_known_values(self):
        cases = {
            10: "a",
            61: "Z",
            62: "10",
            3843: "ZZ",
            3844: "100",
        }
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(encode(number), expected)

    def test_decode_known_values(self):
        cases = {
            "0": 0,
            "a": 10,
            "Z": 61,
            "10": 62,
            "ZZ": 3843,
            "100": 3844,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(decode(text), expected)

    def test_round_trip(self):
        for number in (0, 1, 61, 62, 3843, 3844, 10**30):
            with self.subTest(number=number):
                self.assertEqual(decode(encode(number)), number)

    def test_encode_rejects_negative_and_invalid_types(self):
        with self.assertRaises(ValueError):
            encode(-1)
        with self.assertRaises(TypeError):
            encode(1.5)
        with self.assertRaises(TypeError):
            encode(True)

    def test_decode_rejects_invalid_input(self):
        for text in ("", "0_1", "-1"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    decode(text)
        with self.assertRaises(TypeError):
            decode(62)


if __name__ == "__main__":
    unittest.main()
