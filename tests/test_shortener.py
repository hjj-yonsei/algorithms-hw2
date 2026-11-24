import unittest
from src.shortener import URLShortener


class TestShortenerChaining(unittest.TestCase):
    def test_shorten_and_resolve(self):
        s = URLShortener()
        code1 = s.shorten("https://www.yonsei.ac.kr")
        code2 = s.shorten("https://github.com")
        self.assertNotEqual(code1, code2)
        self.assertEqual(s.resolve(code1), "https://www.yonsei.ac.kr")
        self.assertEqual(s.resolve(code2), "https://github.com")

    def test_duplicate_url_returns_same_code(self):
        s = URLShortener()
        first = s.shorten("https://www.yonsei.ac.kr")
        second = s.shorten("https://www.yonsei.ac.kr")
        self.assertEqual(first, second)
        self.assertEqual(len(s), 1)

    def test_invalid_urls_raise_value_error(self):
        s = URLShortener()
        invalid_urls = [
            "",
            "   ",
            "ftp://files.example.com",
            "javascript:alert(1)",
            "https://",
            "http:///only-path",
            "https://example.com/has space",
            "https://example.com/" + ("a" * 2050),
        ]
        for bad in invalid_urls:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    s.shorten(bad)

    def test_unknown_or_invalid_code_returns_none(self):
        s = URLShortener()
        self.assertIsNone(s.resolve(""))
        self.assertIsNone(s.resolve("nonexistent"))
        self.assertIsNone(s.resolve("bad-code!"))


if __name__ == "__main__":
    unittest.main()
