import unittest

from src.base62 import encode
from src.shortener import URLShortener


class TestURLShortener(unittest.TestCase):
    def test_first_code_is_one_in_base62(self):
        shortener = URLShortener(table_type="chaining", capacity=11)

        code = shortener.shorten("https://example.com")

        self.assertEqual(code, encode(1))

    def test_duplicate_url_returns_existing_code(self):
        shortener = URLShortener(table_type="chaining", capacity=11)

        first = shortener.shorten("https://example.com")
        second = shortener.shorten("https://example.com")

        self.assertEqual(first, second)
        self.assertEqual(shortener.resolve(first), "https://example.com")

    def test_different_urls_receive_different_codes(self):
        shortener = URLShortener(table_type="chaining", capacity=11)

        first = shortener.shorten("https://example.com/a")
        second = shortener.shorten("https://example.com/b")

        self.assertNotEqual(first, second)
        self.assertEqual(shortener.resolve(first), "https://example.com/a")
        self.assertEqual(shortener.resolve(second), "https://example.com/b")

    def test_invalid_schemes_and_hosts_are_rejected(self):
        shortener = URLShortener(table_type="chaining", capacity=11)
        invalid_urls = [
            "",
            "ftp://example.com",
            "javascript:alert(1)",
            "http://",
            "https://",
            " https://example.com",
            "https://example.com ",
            "https://exa mple.com",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    shortener.shorten(url)

    def test_url_over_length_limit_is_rejected(self):
        shortener = URLShortener(table_type="chaining", capacity=11)
        url = "https://example.com/" + ("a" * 2048)

        with self.assertRaises(ValueError):
            shortener.shorten(url)

    def test_missing_and_invalid_codes_return_none(self):
        shortener = URLShortener(table_type="chaining", capacity=11)

        self.assertIsNone(shortener.resolve(""))
        self.assertIsNone(shortener.resolve("not-a-base62-code"))
        self.assertIsNone(shortener.resolve("unknown"))

    def test_chaining_and_linear_modes_have_matching_behavior(self):
        url = "https://example.com/page"

        for table_type in ("chaining", "linear"):
            with self.subTest(table_type=table_type):
                shortener = URLShortener(
                    table_type=table_type,
                    capacity=11,
                    max_load=0.75,
                )
                code = shortener.shorten(url)

                self.assertEqual(shortener.resolve(code), url)
                duplicate = shortener.shorten(url)
                self.assertEqual(duplicate, code)

    def test_linear_mode_rejects_invalid_urls(self):
        shortener = URLShortener(
            table_type="linear",
            capacity=11,
            max_load=0.75,
        )

        with self.assertRaises(ValueError):
            shortener.shorten("ftp://example.com")
        with self.assertRaises(ValueError):
            shortener.shorten("https://")


if __name__ == "__main__":
    unittest.main()
