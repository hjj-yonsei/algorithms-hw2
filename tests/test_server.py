import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPRedirectHandler, Request, urlopen

from src.server import make_server
from src.shortener import URLShortener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.service = URLShortener(table_type="chaining", capacity=11, max_load=0.75)
        self.server = make_server("127.0.0.1", 0, self.service)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_form_and_post_form(self):
        with urlopen(self.base_url + "/", timeout=2) as response:
            page = response.read().decode("utf-8")
            self.assertIn("URL 단축기", page)
            self.assertIn('name="url"', page)

        data = urlencode({"url": "https://example.com/path"}).encode("utf-8")
        request = Request(
            self.base_url + "/shorten",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(request, timeout=2) as response:
            page = response.read().decode("utf-8")
            self.assertIn("짧은 링크가 생성되었습니다.", page)

    def test_redirect_and_table(self):
        code = self.service.shorten("https://example.com")
        opener = build_opener(NoRedirect)
        try:
            opener.open(self.base_url + "/" + code, timeout=2)
        except HTTPError as exc:
            self.assertEqual(exc.code, 302)
            self.assertEqual(exc.headers["Location"], "https://example.com")

        with urlopen(self.base_url + "/table", timeout=2) as response:
            page = response.read().decode("utf-8")
            self.assertIn("해시 테이블 시각화", page)
            self.assertIn("https://example.com", page)
            self.assertIn("호너 해시 계산 펼치기", page)
            self.assertIn("→ NULL", page)


if __name__ == "__main__":
    unittest.main()
