"""Standard-library web interface for the URL shortener."""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from html import escape

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hash_table import horner_steps
from src.shortener import URLShortener


shortener = URLShortener(table_type="chaining", capacity=11, max_load=0.75)


def _first_forwarded(value):
    if not value:
        return None
    return value.split(",", 1)[0].strip()


def _base_url(handler):
    proto = _first_forwarded(handler.headers.get("X-Forwarded-Proto"))
    host = _first_forwarded(handler.headers.get("X-Forwarded-Host"))
    if proto not in ("http", "https"):
        proto = "http"
    if not host:
        host = handler.headers.get("Host")
    if not host:
        host = handler.server.server_address[0]
        port = handler.server.server_address[1]
        host = f"{host}:{port}"
    return f"{proto}://{host}"


def _horner_details(key, capacity):
    steps = horner_steps(key, capacity)
    if not steps:
        return "<p>빈 문자열: 초기 h = 0 → 최종 h = 0 mod M = 0</p>"

    rows = []
    h = 0
    for char, ord_value, previous, current in steps:
        rows.append(
            "<li>"
            f"<code>{escape(repr(char))}</code>, ord = {ord_value}: "
            f"h = (31 × {previous} + {ord_value}) mod {capacity} "
            f"{previous} × 31 + {ord_value} = {31 * previous + ord_value}"
            f" → {current}"
            "</li>"
        )
        h = current
    return (
        "<p>초기 h = 0</p><ol>"
        + "".join(rows)
        + f"</ol><p><strong>최종 해시 = {h}</strong></p>"
    )


def _page(title, body):
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
    body {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #24292f; }}
    nav {{ margin-bottom: 2rem; }}
    nav a {{ margin-right: 1rem; }}
    form {{ display: flex; gap: .5rem; max-width: 900px; }}
    input[type=url] {{ flex: 1; padding: .7rem; font-size: 1rem; }}
    button {{ padding: .7rem 1rem; }}
    .result {{ margin-top: 1.5rem; padding: 1rem; background: #ddf4ff; border-radius: 6px; }}
    .error {{ color: #cf222e; }}
    .bucket {{ display: grid; grid-template-columns: 70px 1fr; gap: 1rem;
               border: 1px solid #d0d7de; border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
    .bucket-index {{ font-weight: bold; }}
    .chain {{ display: flex; align-items: center; flex-wrap: wrap; gap: .6rem; }}
    .node {{ min-width: 220px; max-width: 600px; border: 1px solid #0969da;
             border-radius: 6px; padding: .7rem; background: #f6f8fa; }}
    .node strong {{ display: block; overflow-wrap: anywhere; }}
    .arrow {{ color: #57606a; font-weight: bold; }}
    details {{ margin-top: .5rem; }}
  </style>
</head>
<body>
  <nav><a href="/">줄이기</a><a href="/table">해시 테이블</a></nav>
  {body}
</body>
</html>"""


def _form_page(error=None, code=None, short_link=None, original_url=None):
    result = ""
    if error:
        result = f'<p class="error">{escape(error)}</p>'
    elif code:
        result = (
            '<div class="result">'
            "<p>짧은 링크가 생성되었습니다.</p>"
            f'<a href="{escape(short_link)}">{escape(short_link)}</a>'
            f"<p>원본 주소: {escape(original_url)}</p>"
            "</div>"
        )
    body = f"""
  <h1>URL 단축기</h1>
  <form method="post" action="/shorten">
    <input type="url" name="url" placeholder="https://example.com/" required>
    <button type="submit">줄이기</button>
  </form>
  {result}
"""
    return _page("URL 단축기", body)


def _table_page(table, base_url):
    if hasattr(table, "slots"):
        rows = []
        for index, key in enumerate(table.slots):
            if not isinstance(key, str):
                rows.append(
                    '<section class="bucket">'
                    f'<div class="bucket-index">[{index}]</div>'
                    '<div class="chain"><div class="node"><em>빈 칸 또는 삭제 표시</em></div></div>'
                    "</section>"
                )
                continue
            value = table.values[index]
            short_link = f"{base_url}/{value}"
            steps = _horner_details(key, table.capacity)
            rows.append(
                '<section class="bucket">'
                f'<div class="bucket-index">[{index}]</div>'
                '<div class="chain">'
                '<div class="node">'
                f"<strong>URL 키</strong><div>{escape(key)}</div>"
                f"<strong>짧은 코드</strong><div>{escape(str(value))}</div>"
                f'<strong>짧은 링크</strong><div><a href="{escape(short_link)}">{escape(short_link)}</a></div>'
                f"<details><summary>호너 해시 계산 펼치기</summary>{steps}</details>"
                "</div></div></section>"
            )
        body = (
            "<h1>해시 테이블 시각화</h1>"
            f"<p>선형 탐지 · 용량 {table.capacity} · 저장 원소 {len(table)}</p>"
            + "".join(rows)
        )
        return _page("해시 테이블", body)

    rows = []
    for index, node in enumerate(table.buckets):
        chain = []
        node_count = 0
        while node is not None:
            node_count += 1
            short_link = f"{base_url}/{node.value}"
            steps = _horner_details(node.key, table.capacity)
            chain.append(
                '<div class="node">'
                f"<strong>URL 키</strong><div>{escape(node.key)}</div>"
                f"<strong>짧은 코드</strong><div>{escape(node.value)}</div>"
                f'<strong>짧은 링크</strong><div><a href="{escape(short_link)}">{escape(short_link)}</a></div>'
                f"<details><summary>호너 해시 계산 펼치기</summary>{steps}</details>"
                "</div>"
            )
            node = node.next
            if node is not None:
                chain.append('<span class="arrow">→</span>')
        if not chain:
            chain.append('<div class="node"><em>빈 칸 (NULL)</em></div>')
        else:
            chain.append('<span class="arrow">→ NULL</span>')
        rows.append(
            '<section class="bucket">'
            f'<div class="bucket-index">[{index}]<br><small>{node_count} node(s)</small></div>'
            f'<div class="chain">{''.join(chain)}</div>'
            "</section>"
        )
    body = (
        "<h1>해시 테이블 시각화</h1>"
        f"<p>체이닝 · 용량 {table.capacity} · 저장 원소 {len(table)}</p>"
        + "".join(rows)
    )
    return _page("해시 테이블", body)


class ShortURLHandler(BaseHTTPRequestHandler):
    server_version = "ShortURLServer/1.0"

    def _service(self):
        return getattr(self, "_shortener", shortener)

    def _send_html(self, status, body):
        content = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self._send_html(200, _form_page())
            return
        if path == "/table":
            self._send_html(
                200,
                _table_page(self._service().url_to_code, _base_url(self)),
            )
            return

        code = path[1:] if path.startswith("/") else ""
        if "/" in code:
            self.send_error(404, "Not Found")
            return
        original_url = self._service().resolve(code)
        if original_url is None:
            self.send_error(404, "Unknown short code")
            return
        self.send_response(302)
        self.send_header("Location", original_url)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/", "/shorten"):
            self.send_error(404, "Not Found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()

        url = None
        if content_type == "application/json":
            try:
                payload = json.loads(body.decode("utf-8"))
                if hasattr(payload, "get"):
                    url = payload.get("url")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        else:
            try:
                form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
            except UnicodeDecodeError:
                form = None
            values = form.get("url") if form is not None else None
            if values:
                url = values[0]

        if url is None:
            self._send_html(400, _form_page(error="유효한 url 값이 필요합니다."))
            return

        try:
            code = self._service().shorten(url)
        except ValueError as exc:
            self._send_html(400, _form_page(error=str(exc)))
            return

        short_link = f"{_base_url(self)}/{code}"
        if content_type == "application/json":
            payload = (
                '{"code":'
                + json.dumps(code)
                + ',"url":'
                + json.dumps(url, ensure_ascii=False)
                + ',"short_link":'
                + json.dumps(short_link, ensure_ascii=False)
                + "}"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self._send_html(
            200,
            _form_page(code=code, short_link=short_link, original_url=url),
        )


def make_handler(service=None):
    service_for_server = service

    class ConfiguredShortURLHandler(ShortURLHandler):
        pass

    if service_for_server is not None:
        ConfiguredShortURLHandler._shortener = service_for_server
    return ConfiguredShortURLHandler


def make_server(host="127.0.0.1", port=8000, service=None):
    handler = make_handler(service)
    return ThreadingHTTPServer((host, port), handler)


def main():
    parser = argparse.ArgumentParser(description="URL 단축 웹 서버")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), ShortURLHandler)
    print(f"URL 단축 서버 실행 중: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
